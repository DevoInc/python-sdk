import os
import select
import socket
import tempfile
from pathlib import Path
from ssl import CERT_NONE, SSLSocket, SSLWantReadError
from unittest import mock

import pem
import pytest
from helpers.local_servers import (SSLServer, TCPServer, find_available_port,
                                   wait_for_ready_server)
from OpenSSL import SSL, crypto

from devo.common import Configuration, get_log
from devo.common.loadenv.load_env import load_env_file
from devo.sender import (DevoSenderException, Sender, SenderConfigSSL,
                         SenderConfigTCP)
from devo.sender.data import open_file

TEST_FACILITY = 10

# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


@pytest.fixture(scope="module", autouse=True)
def setup():

    class Fixture:
        pass

    setup = Fixture()

    # Server configuration
    # ----------------------------------------
    setup.ssl_address = os.getenv("DEVO_SENDER_SERVER", "127.0.0.1")
    setup.ssl_port = int(os.getenv("DEVO_SENDER_PORT", 4488))
    setup.tcp_address = os.getenv("DEVO_SENDER_TCP_SERVER", "127.0.0.1")
    setup.tcp_port = int(os.getenv("DEVO_SENDER_TCP_PORT", 4489))
    setup.remote_address = os.getenv("DEVO_REMOTE_SENDER_SERVER", "collector-us.devo.io")
    setup.remote_port = int(os.getenv("DEVO_REMOTE_SENDER_PORT", 443))

    # Resources configuration
    # ----------------------------------------
    setup.res_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "resources"
    setup.my_app = "test.drop.free"
    setup.my_bapp = b"test.drop.free"
    setup.my_date = "my.date.test.sender"
    setup.test_file = setup.res_path + os.sep + "testfile_multiline.txt"
    setup.lookup_file = setup.res_path + os.sep + "testfile_lookup_with_quotes.csv"
    setup.lookup_name = "TEST_LOOKUP"
    setup.test_msg = "Test send msg\n"
    setup.localhost = socket.gethostname()
    setup.default_numbers_sendings = 10  # change this value if you want

    # Certificates configuration - LOCAL SERVER
    # ----------------------------------------
    setup.certs_path = setup.res_path + os.sep + "local_certs" + os.sep + "keys"
    setup.local_server_key = os.getenv(
        "DEVO_SENDER_SERVER_KEY", f"{setup.certs_path}/server/private/server_key.pem"
    )
    setup.local_server_cert = os.getenv(
        "DEVO_SENDER_SERVER_CERT", f"{setup.certs_path}/server/server_cert.pem"
    )
    setup.local_server_chain = os.getenv(
        "DEVO_SENDER_SERVER_CHAIN", f"{setup.certs_path}/ca/ca_cert.pem"
    )
    setup.test_tcp = os.getenv("DEVO_TEST_TCP", False)
    setup.configuration = Configuration()
    setup.configuration.set(
        "sender",
        {
            "key": setup.local_server_key,
            "cert": setup.local_server_cert,
            "chain": setup.local_server_chain,
            "address": setup.ssl_address,
            "port": setup.ssl_port,
            "verify_mode": 0,
            "check_hostname": False,
        },
    )

    # Certificates configuration - REMOTE SERVER
    # ----------------------------------------
    setup.remote_server_key = os.getenv(
        "DEVO_SENDER_KEY", f"{setup.res_path}/certs/us/devo_services.key"
    )
    setup.remote_server_cert = os.getenv(
        "DEVO_SENDER_CERT", f"{setup.res_path}/certs/us/devo_services.crt"
    )
    setup.remote_server_chain = os.getenv(
        "DEVO_SENDER_CHAIN", f"{setup.res_path}/certs/us/chain.crt"
    )

    # Configuration files
    # ----------------------------------------
    setup.config_path = os.path.join(tempfile.gettempdir(), "devo_api_tests_config.json")
    setup.configuration.save(path=setup.config_path)

    # Run local servers
    # ----------------------------------------
    setup.ssl_port = find_available_port(setup.ssl_address, setup.ssl_port)
    local_ssl_server = SSLServer(
        setup.ssl_address, setup.ssl_port, setup.local_server_cert, setup.local_server_key
    )
    wait_for_ready_server(local_ssl_server.ip, local_ssl_server.port)

    if setup.test_tcp:
        setup.tcp_port = find_available_port(setup.tcp_address, setup.tcp_port)
        local_tcp_server = TCPServer(setup.tcp_address, setup.tcp_port)
        wait_for_ready_server(local_tcp_server.ip, local_tcp_server.port)

    yield setup

    local_ssl_server.close_server()
    local_tcp_server.close_server() if setup.test_tcp else None


def _read(con, length: int):
    if not select.select([con.socket], [], [], con.socket_timeout)[0]:
        raise TimeoutError("Timeout reached during read operation")
    if isinstance(con.socket, SSLSocket):
        while True:
            try:
                return con.socket.recv(length)
            except SSLWantReadError:
                # If the data is ready at socket OS level but not at
                # SSL wrapper level, this exception may raise
                pass
    return con.socket.recv(length)


def test_compose_mem(setup):
    assert Sender.compose_mem("test.tag") == "<14>Jan  1 00:00:00 %s test.tag: " % setup.localhost

    assert (
        Sender.compose_mem("test.tag", hostname="my-pc") == "<14>Jan  1 00:00:00 my-pc test.tag: "
    )

    assert (
        Sender.compose_mem("test.tag", date="1991-02-20 12:00:00")
        == "<14>1991-02-20 12:00:00 %s test.tag: " % setup.localhost
    )

    assert Sender.compose_mem(
        b"test.tag", bytes=True
    ) == b"<14>Jan  1 00:00:00 %s test.tag: " % setup.localhost.encode("utf-8")

    assert (
        Sender.compose_mem(b"test.tag", hostname=b"my-pc", bytes=True)
        == b"<14>Jan  1 00:00:00 my-pc test.tag: "
    )

    assert Sender.compose_mem(
        b"test.tag", date=b"1991-02-20 12:00:00", bytes=True
    ) == b"<14>1991-02-20 12:00:00 %s test.tag: " % setup.localhost.encode("utf-8")


def test_tcp_rt_send(setup):
    """
    Tests that a TCP connection and data send it is possible
    """
    if not setup.test_tcp:
        pytest.skip("Not testing TCP")

    try:
        engine_config = SenderConfigTCP(address=(setup.tcp_address, setup.tcp_port))
        con = Sender(engine_config)
        for i in range(setup.default_numbers_sendings):
            con.send(tag=setup.my_app, msg=setup.test_msg)
            if len(_read(con, 5000)) == 0:
                raise Exception("Not msg sent!")
        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % error)


def test_ssl_rt_send(setup):
    """
    Test that tries to send a message through a ssl connection
    """
    try:
        engine_config = SenderConfigSSL(
            address=(setup.ssl_address, setup.ssl_port),
            key=setup.local_server_key,
            cert=setup.local_server_cert,
            chain=setup.local_server_chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender(engine_config)
        for i in range(setup.default_numbers_sendings):
            con.send(tag=setup.my_app, msg=setup.test_msg)
            data_received = _read(con, 5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception("Not msg sent!")
        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % str(error))


def test_ssl_zip_send(setup):
    """
    Test that tries to send a message through a ssl connection
    """
    try:
        engine_config = SenderConfigSSL(
            address=(setup.ssl_address, setup.ssl_port),
            key=setup.local_server_key,
            cert=setup.local_server_cert,
            chain=setup.local_server_chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender(engine_config, timeout=15)
        for i in range(setup.default_numbers_sendings):
            con.send(tag=setup.my_bapp, msg=setup.test_msg.encode("utf-8"), zip=True)
            con.flush_buffer()
            data_received = _read(con, 5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception("Not msg sent!")
        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % str(error))


def test_multiline_send(setup):
    """
    Test that tries to send a multiple line message through
    a ssl connection
    """
    try:
        engine_config = SenderConfigSSL(
            address=(setup.ssl_address, setup.ssl_port),
            key=setup.local_server_key,
            cert=setup.local_server_cert,
            chain=setup.local_server_chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender(engine_config)
        with open(setup.test_file, "r") as file:
            content = file.read()

        con.send(tag=setup.my_app, msg=content, multiline=True)
        con.flush_buffer()
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")
        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % error)


def test_rt_send_no_certs(setup):
    """
    Test that tries to send a message without using certificates
    """
    if not setup.test_tcp:
        pytest.skip("Not testing TCP")
    try:
        engine_config = SenderConfigSSL(
            address=(setup.ssl_address, setup.ssl_port),
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender(engine_config)
        for i in range(setup.default_numbers_sendings):
            con.send(tag=setup.my_app, msg=setup.test_msg)
        con.close()
        return True
    except Exception:
        return False


def test_sender_as_handler(setup):
    """
    Test that tries to check that Sender class can be used as a Handler
    and related logs are send to remote server
    """
    try:
        engine_config = SenderConfigSSL(
            address=(setup.ssl_address, setup.ssl_port),
            key=setup.local_server_key,
            cert=setup.local_server_cert,
            chain=setup.local_server_chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender.for_logging(config=engine_config, tag=setup.my_app, level=TEST_FACILITY)
        logger = get_log(name="DevoLogger", handler=con, level=TEST_FACILITY)
        print("Testing logger info")
        logger.info("Testing Sender inherit logging handler functionality... INFO - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger error")
        logger.error("Testing Sender inherit logging handler functionality... ERROR - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger warning")
        logger.warning("Testing Sender inherit logging handler functionality... WARNING - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger debug")
        logger.debug("Testing Sender inherit logging handler functionality... DEBUG - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger critical")
        logger.critical("Testing Sender inherit logging handler functionality... CRITICAL - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % str(error))


def test_sender_with_default_logger(setup):
    """
    Test that tries to check that Sender class can still use an internal
    logger and shows both local and remote
    traces
    """
    try:
        engine_config = SenderConfigSSL(
            address=(setup.ssl_address, setup.ssl_port),
            key=setup.local_server_key,
            cert=setup.local_server_cert,
            chain=setup.local_server_chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender.for_logging(config=engine_config, tag=setup.my_app, level=TEST_FACILITY)
        # NOTE: this logger logging traces will be visible in console
        con.logger.info(
            "Testing Sender default handler functionality in local console... INFO - log"
        )
        # NOTE: this logger logging traces will be visible in the remote
        # table
        con.info("Testing Sender default handler functionality in remote table... INFO - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % str(error))


def test_sender_as_handler_static(setup):
    """
    Test that tries to check that Sender class can be used as a Handler
    through the static functions
    and related logs are send to remote server
    """
    try:
        engine_config = {
            "address": setup.ssl_address,
            "port": setup.ssl_port,
            "key": setup.local_server_key,
            "cert": setup.local_server_cert,
            "chain": setup.local_server_chain,
            "check_hostname": False,
            "verify_mode": CERT_NONE,
        }

        con = Sender.for_logging(config=engine_config, tag=setup.my_app, level=TEST_FACILITY)
        logger = get_log(name="DevoLogger2", handler=con, level=TEST_FACILITY)

        print("Testing logger info")
        logger.info("Testing Sender static handler functionality... INFO - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger error")
        logger.error("Testing Sender static logging handler functionality... ERROR - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger warning")
        logger.warning("Testing Sender static logging handler functionality... WARNING - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger debug")
        logger.debug("Testing Sender static logging handler functionality... DEBUG - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        print("Testing logger critical")
        logger.critical("Testing Sender static logging handler functionality... CRITICAL - log")
        data_received = _read(con, 5000)
        print(b"\n" + data_received)
        if len(data_received) == 0:
            raise Exception("Not msg sent!")

        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % str(error))


def test_config_files_path_standard_case(setup):
    """
    Test that verifies that a correct path for the
    configuration file is detected.
    """

    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    result = engine_config.check_config_files_path()
    assert result is True


def test_config_files_path_incorrect_key(setup):
    """
    Test that verifies that an incorrect path for the
    configuration raises an exception.
    """
    wrong_key = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key="Incorrect key",
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    wrong_key_message = (
        "Error in the configuration, "
        + "Incorrect key"
        + " is not a file or the path does not exist"
    )

    with pytest.raises(DevoSenderException) as result:
        wrong_key.check_config_files_path()

    assert wrong_key_message == str(result.value.message)


def test_config_files_path_incorrect_cert(setup):
    wrong_cert = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert="Incorrect cert",
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    wrong_cert_message = (
        "Error in the configuration, "
        + "Incorrect cert"
        + " is not a file or the path does not exist"
    )

    with pytest.raises(DevoSenderException) as result:
        wrong_cert.check_config_files_path()

    assert wrong_cert_message == str(result.value.message)


def test_config_files_path_incorrect_chain(setup):
    wrong_chain = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain="Incorrect chain",
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )
    wrong_chain_message = (
        "Error in the configuration, "
        + "Incorrect chain"
        + " is not a file or the path does not exist"
    )

    with pytest.raises(DevoSenderException) as result:
        wrong_chain.check_config_files_path()

    assert wrong_chain_message == str(result.value.message)


def test_config_cert_key_standard_case(setup):
    """
    Test that verifies that a compatible certificate
    and key are detected.
    """

    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )
    result = engine_config.check_config_certificate_key()
    assert result is True


def test_config_cert_key_incompatible_case(setup):
    """
    Test that verifies that an incompatible
    certificate with a key raises an exception.
    """

    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.remote_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    with pytest.raises(DevoSenderException) as result:
        engine_config.check_config_certificate_key()

    expected_exception = (
        "Error in the configuration, the key: "
        + engine_config.key
        + " is not compatible with the cert: "
        + engine_config.cert
    )

    assert expected_exception in str(result.value.message)


def test_config_cert_chain_standard_case(setup):
    """
    Test that verifies that a compatible certificate
    and chain are detected.
    """

    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )
    result = engine_config.check_config_certificate_chain()
    assert result is True


def test_config_cert_chain_incompatible_case(setup):
    """
    Test that verifies that an incompatible
    certificate with a chain raises an exception.
    """

    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.remote_server_cert,
        # chain="{!s}/local_certs/keys/server/server_cert.pem".format(
        #     os.path.dirname(os.path.abspath(__file__))
        # ),
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    with pytest.raises(DevoSenderException) as result:
        engine_config.check_config_certificate_chain()

    expected_exception = (
        "Error in config, "
        "the chain: " + engine_config.chain + " is not compatible with "
        "the certificate: " + engine_config.cert
    )

    assert expected_exception in str(result.value.message)


def test_config_cert_address_standard_case(setup):
    """
    Test that verifies that a compatible certificate
    and address are detected.
    """
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )
    chain = engine_config.fake_get_peer_cert_chain(setup.local_server_chain)
    with mock.patch.object(
        SSL.Connection, "get_peer_cert_chain", mock.MagicMock(return_value=chain)
    ):
        result = engine_config.check_config_certificate_address()
        assert result is True


def test_config_cert_address_incompatible_address(setup):
    """
    Test that verifies that an incompatible certificate
    and address raises an exception.
    """
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.remote_server_key,
        cert=setup.remote_server_cert,
        chain=setup.remote_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    with pytest.raises(DevoSenderException) as result:
        engine_config.check_config_certificate_address()

    expected_exception = (
        "Error in config, "
        + "the certificate in the address: "
        + engine_config.address[0]
        + " is not compatible with: "
        + engine_config.chain
    )

    assert expected_exception in str(result.value.message)


def test_config_cert_address_incompatible_port(setup):
    """
    Test that verifies that a wrong port raises an exception.
    """
    remote_address = os.getenv("DEVO_REMOTE_SENDER_SERVER", "collector-us.devo.io")
    engine_config = SenderConfigSSL(
        address=(remote_address, 442),
        key=setup.remote_server_key,
        cert=setup.remote_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    with pytest.raises(DevoSenderException) as result:
        engine_config.check_config_certificate_address()

    expected_exception = (
        "Possible error in config, "
        "a timeout could be related "
        + "to an incorrect address/port: "
        + str(engine_config.address)
    )

    assert expected_exception in str(result.value.message)


def test_get_common_names(setup):
    """
    Verify Subject and Issuer Names:
    Confirm that the issuer of each certificate matches the subject of the next certificate
    in the chain. This ensures that each certificate is properly linked in the chain.
    """
    engine_config = SenderConfigSSL(
        address=("localhost", 442),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )
    server_chain = engine_config.fake_get_peer_cert_chain(setup.local_server_chain)
    chain_cert = engine_config.fake_get_peer_cert_chain(setup.local_server_cert)
    subject = engine_config.get_common_names(server_chain, "get_subject")
    issuer = engine_config.get_common_names(chain_cert, "get_issuer")

    assert issuer.issubset(subject) is True


def test_fake_get_peer_cert_chain(setup):
    engine_config = SenderConfigSSL(
        address=("localhost", 442),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
        verify_config=False,
    )

    fake_chain_cert = engine_config.fake_get_peer_cert_chain(setup.local_server_chain)
    with open(setup.local_server_chain, "rb") as chain_file:
        chain_certs = []
        for _ca in pem.parse(chain_file.read()):
            chain_certs.append(crypto.load_certificate(crypto.FILETYPE_PEM, str(_ca)))

    for a, b in zip(fake_chain_cert, chain_certs):
        assert a.get_subject() == b.get_subject()


def test_open_file(setup):
    with pytest.raises(FileNotFoundError):
        open_file(Path("wrong_file"), mode="r", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        open_file("wrong_file", mode="r", encoding="utf-8")
    with pytest.raises(DevoSenderException):
        open_file(55, mode="r", encoding="utf-8")


if __name__ == "__main__":
    pytest.main()
