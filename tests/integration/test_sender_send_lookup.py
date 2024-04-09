import os
import select
import socket
import tempfile
from ssl import CERT_NONE
from unittest import mock

import pytest

from devo.common import Configuration
from devo.common.loadenv.load_env import load_env_file
from devo.sender import Lookup, Sender, SenderConfigSSL

from .local_servers import (SSLServer, find_available_port,
                            wait_for_ready_server)


def _read(con, length: int):
    if not select.select([con.socket], [], [], con.socket_timeout)[0]:
        raise TimeoutError("Timeout reached during read operation")
    return con.socket.recv(length)


# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


@pytest.fixture(scope="module", autouse=True)  # noqa: F821
def setup():

    class Fixture:
        pass

    setup = Fixture()

    # Server configuration
    # ----------------------------------------
    setup.ssl_address = os.getenv("DEVO_SENDER_SERVER", "127.0.0.1")
    setup.ssl_port = int(os.getenv("DEVO_SENDER_PORT", 4488))
    setup.remote_address = os.getenv("DEVO_REMOTE_SENDER_SERVER", "collector-us.devo.io")
    setup.remote_port = int(os.getenv("DEVO_REMOTE_SENDER_PORT", 443))

    # Resources configuration
    # ----------------------------------------
    setup.res_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "resources"
    setup.my_app = "test.drop.free"
    setup.my_bapp = b"test.drop.free"
    setup.my_date = "my.date.test.sender"
    setup.test_file = setup.res_path + os.sep + "testfile_multiline.txt"
    setup.lookup_file = setup.res_path + os.sep + "testfile_lookup.csv"
    setup.lookup_name = "TEST_LOOKUP"
    setup.test_msg = "Test send msg\n"
    setup.localhost = socket.gethostname()
    setup.default_numbers_sendings = 10  # change this value if you want
    setup.lookup_key = "KEY"

    # Certificates configuration - LOCAL SERVER
    # ----------------------------------------
    setup.certs_path = setup.res_path + os.sep + "local_certs" + os.sep + "keys"
    setup.local_server_key = os.getenv(
        "DEVO_SENDER_SERVER_KEY", f"{setup.certs_path}/server/private/server_key.pem"
    )
    setup.local_server_cert = os.getenv(
        "DEVO_SENDER_SERVER_CRT", f"{setup.certs_path}/server/server_cert.pem"
    )
    setup.local_server_chain = os.getenv(
        "DEVO_SENDER_SERVER_CHAIN", f"{setup.certs_path}/ca/ca_cert.pem"
    )

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

    setup.ssl_port = find_available_port(setup.ssl_address, setup.ssl_port)
    local_ssl_server = SSLServer(
        setup.ssl_address, setup.ssl_port, setup.local_server_cert, setup.local_server_key
    )

    wait_for_ready_server(local_ssl_server.ip, local_ssl_server.port)

    yield setup

    local_ssl_server.close_server()


def test_ssl_lookup_csv_send(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
    )
    con = Sender(engine_config)
    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con)

    with open(setup.lookup_file) as f:
        line = f.readline()

    lookup.send_csv(
        setup.lookup_file,
        headers=line.rstrip().split(","),
        key=setup.lookup_key,
    )

    con.socket.shutdown(0)


# Add new line to lookup
def test_ssl_lookup_new_line(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
    )

    con = Sender(engine_config)

    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con)
    p_headers = Lookup.list_to_headers(["KEY", "HEX", "COLOR"], "KEY")
    lookup.send_control("START", p_headers, "INC")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_data_line(key_index=0, fields=["11", "HEX12", "COLOR12"])
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_control("END", p_headers, "INC")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")

    con.socket.shutdown(0)


def test_create_lookup_key_index_preserves_structure(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
    )
    con = Sender(engine_config)
    lookup = Lookup(name=setup.lookup_name, con=con)
    headers = ["col1", "col2", "col3"]
    fields = ["a", "b", "c"]

    expected_headers = (
        '[{"col1":{"type":"str","key":true}},' + '{"col2":{"type":"str"}},{"col3":{"type":"str"}}]'
    )
    with mock.patch.object(lookup, "send_control", wraps=lookup.send_control) as lookup_spy:
        lookup.send_headers(headers=headers, key_index=0, event="START", action="FULL")
        lookup_spy.assert_called_with(action="FULL", event="START", headers=expected_headers)
        lookup.send_data_line(key_index=0, fields=fields)
        lookup.send_headers(headers=headers, key_index=0, event="END", action="FULL")
        lookup_spy.assert_called_with(action="FULL", event="END", headers=expected_headers)
    con.socket.shutdown(0)


def test_send_headers_with_type_of_key(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
    )
    con = Sender(engine_config)
    lookup = Lookup(name=setup.lookup_name, con=con)
    headers = ["col1", "col2", "col3"]

    expected_headers = (
        '[{"col1":{"type":"int4","key":true}},'
        + '{"col2":{"type":"str"}},{"col3":{"type":"str"}}]'
    )
    with mock.patch.object(lookup, "send_control", wraps=lookup.send_control) as lookup_spy:
        lookup.send_headers(
            headers=headers,
            key_index=0,
            type_of_key="int4",
            event="START",
            action="FULL",
        )
        lookup_spy.assert_called_with(action="FULL", event="START", headers=expected_headers)
    con.socket.shutdown(0)


# add new line deleting previous data
def test_ssl_lookup_override(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
    )
    con = Sender(engine_config)
    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con)
    p_headers = Lookup.list_to_headers(["KEY", "HEX", "COLOR"], "KEY")
    lookup.send_control("START", p_headers, "FULL")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_data_line(key_index=0, fields=["11", "HEX12", "COLOR12"])
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_control("END", p_headers, "FULL")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    con.socket.shutdown(0)


# delete a line from lookup
def test_ssl_lookup_delete_line(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
    )
    con = Sender(engine_config)

    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con)
    p_headers = Lookup.list_to_headers(["KEY", "HEX", "COLOR"], "KEY")
    lookup.send_control("START", p_headers, "INC")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_data_line(key_index=0, fields=["11", "HEX12", "COLOR12"], delete=True)
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_control("END", p_headers, "INC")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")

    con.socket.shutdown(0)


def test_ssl_lookup_simplify(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
        chain=setup.local_server_chain,
        check_hostname=False,
        verify_mode=CERT_NONE,
    )
    con = Sender(engine_config)

    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con)
    lookup.send_headers(headers=["KEY", "HEX", "COLOR"], key="KEY", action="START")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_data_line(key_index=0, fields=["11", "HEX12", "COLOR12"])
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")
    lookup.send_headers(headers=["KEY", "HEX", "COLOR"], key="KEY", action="END")
    if len(_read(con, 1000)) == 0:
        raise Exception("Not msg sent!")

    con.socket.shutdown(0)


# Test to make sure escape_quotes is propagated correctly
def test_escape_quotes_in_send_data_line_key(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
    )
    con = Sender(engine_config)

    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con, escape_quotes=True)

    with mock.patch.object(Lookup, "clean_field", wraps=Lookup.clean_field) as clean_field:
        lookup.send_data_line(key_index=0, fields=["11", 'Double quotes"'])
        clean_field.assert_called_with('Double quotes"', True)


# Test to make sure escape_quotes is propagated correctly
def test_escape_quotes_in_send_data_line(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
    )
    con = Sender(engine_config)

    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con, escape_quotes=True)

    with mock.patch.object(Lookup, "clean_field", wraps=Lookup.clean_field) as clean_field:
        lookup.send_data_line(key_index=0, fields=["11", 'Double quotes"'])
        clean_field.assert_called_with('Double quotes"', True)

        # Test to make sure escape_quotes is propagated correctly


def test_escape_quotes_in_send_csv(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
    )
    con = Sender(engine_config)

    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con, escape_quotes=True)

    with mock.patch.object(Lookup, "clean_field", wraps=Lookup.clean_field) as clean_field:
        lookup.send_csv(path=setup.lookup_file, has_header=True, key=setup.lookup_key)
        clean_field.assert_called_with("ffffff", True)

        # Test to make sure escape_quotes is propagated correctly


def test_escape_quotes_in_send_csv_delete_index(setup):
    engine_config = SenderConfigSSL(
        address=(setup.ssl_address, setup.ssl_port),
        key=setup.local_server_key,
        cert=setup.local_server_cert,
    )
    con = Sender(engine_config)

    lookup = Lookup(name=setup.lookup_name, historic_tag=None, con=con, escape_quotes=True)

    with mock.patch.object(Lookup, "clean_field", wraps=Lookup.clean_field) as clean_field:
        lookup.send_csv(
            path=setup.lookup_file,
            has_header=True,
            key=setup.lookup_key,
            delete_field="Green",
        )
        clean_field.assert_called_with("ffffff", True)


if __name__ == "__main__":
    pytest.main()
