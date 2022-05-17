import unittest
import socket
from ssl import CERT_NONE

import devo.sender.data
from devo.sender import Sender, SenderConfigTCP, SenderConfigSSL, \
    DevoSenderException
from devo.common import get_log
from .load_certs import *
from unittest import mock
from OpenSSL import SSL
import pem
from OpenSSL import crypto

TEST_FACILITY = 10


class TestSender(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment vars.
        If you have an environment.env file (main directory) it will use it
        to set it else the vars will need to be set
        up in any other way.
        """
        self.server = os.getenv('DEVO_SENDER_SERVER', "127.0.0.1")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 4488))
        self.tcp_server = os.getenv('DEVO_SENDER_TCP_SERVER', "127.0.0.1")
        self.tcp_port = int(os.getenv('DEVO_SENDER_TCP_PORT', 4489))

        self.key = os.getenv('DEVO_SENDER_KEY', CLIENT_KEY)
        self.cert = os.getenv('DEVO_SENDER_CERT', CLIENT_CERT)
        self.chain = os.getenv('DEVO_SENDER_CHAIN', CLIENT_CHAIN)
        self.test_tcp = os.getenv('DEVO_TEST_TCP', "True")
        self.my_app = 'test.drop.free'
        self.my_bapp = b'test.drop.free'
        self.my_date = 'my.date.test.sender'
        self.test_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                                  os.sep, "testfile_multiline.txt"))

        self.test_msg = 'Test send msg\n'
        self.localhost = socket.gethostname()
        # change this value if you want to send another number of test string
        self.default_numbers_sendings = 10

    def test_compose_mem(self):
        self.assertEqual(Sender.compose_mem("test.tag"),
                         '<14>Jan  1 00:00:00 %s test.tag: ' % self.localhost)

        self.assertEqual(Sender.compose_mem("test.tag", hostname="my-pc"),
                         '<14>Jan  1 00:00:00 my-pc test.tag: ')

        self.assertEqual(Sender.compose_mem("test.tag",
                                            date="1991-02-20 12:00:00"),
                         '<14>1991-02-20 12:00:00 %s test.tag: '
                         % self.localhost)

        self.assertEqual(Sender.compose_mem(b"test.tag", bytes=True),
                         b'<14>Jan  1 00:00:00 %s test.tag: '
                         % self.localhost.encode("utf-8"))

        self.assertEqual(Sender.compose_mem(b"test.tag",
                                            hostname=b"my-pc", bytes=True),
                         b'<14>Jan  1 00:00:00 my-pc test.tag: ')

        self.assertEqual(Sender.compose_mem(b"test.tag",
                                            date=b"1991-02-20 12:00:00",
                                            bytes=True),
                         b'<14>1991-02-20 12:00:00 %s test.tag: '
                         % self.localhost.encode("utf-8"))

    def test_tcp_rt_send(self):
        """
        Tests that a TCP connection and data send it is possible
        """
        try:
            engine_config = SenderConfigTCP(address=(self.tcp_server,
                                                     self.tcp_port))
            con = Sender(engine_config)
            for i in range(self.default_numbers_sendings):
                con.send(tag=self.my_app, msg=self.test_msg)
                if len(con.socket.recv(5000)) == 0:
                    raise Exception('Not msg sent!')
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_ssl_rt_send(self):
        """
        Test that tries to send a message through a ssl connection
        """
        try:
            engine_config = SenderConfigSSL(address=(self.server, self.port),
                                            key=self.key, cert=self.cert,
                                            chain=self.chain,
                                            check_hostname=False,
                                            verify_mode=CERT_NONE)
            con = Sender(engine_config)
            for i in range(self.default_numbers_sendings):
                con.send(tag=self.my_app, msg=self.test_msg)
                data_received = con.socket.recv(5000)
                print(b"\n" + data_received)
                if len(data_received) == 0:
                    raise Exception('Not msg sent!')
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % str(error))

    def test_ssl_zip_send(self):
        """
        Test that tries to send a message through a ssl connection
        """
        try:
            engine_config = SenderConfigSSL(address=(self.server, self.port),
                                            key=self.key, cert=self.cert,
                                            chain=self.chain,
                                            check_hostname=False,
                                            verify_mode=CERT_NONE)
            con = Sender(engine_config, timeout=15)
            for i in range(self.default_numbers_sendings):
                con.send(tag=self.my_bapp, msg=self.test_msg.encode("utf-8"),
                         zip=True)
                con.flush_buffer()
                data_received = con.socket.recv(5000)
                print(b"\n" + data_received)
                if len(data_received) == 0:
                    raise Exception('Not msg sent!')
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % str(error))

    def test_multiline_send(self):
        """
        Test that tries to send a multiple line message through a ssl connection
        """
        try:
            engine_config = SenderConfigSSL(address=(self.server, self.port),
                                            key=self.key, cert=self.cert,
                                            chain=self.chain,
                                            check_hostname=False,
                                            verify_mode=CERT_NONE)
            con = Sender(engine_config)
            with open(self.test_file, 'r') as file:
                content = file.read()

            con.send(tag=self.my_app, msg=content, multiline=True)
            con.flush_buffer()
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_rt_send_no_certs(self):
        """
        Test that tries to send a message without using certificates
        """
        if self.test_tcp == "True":
            try:
                engine_config = SenderConfigSSL(address=(self.server,
                                                         self.port),
                                                check_hostname=False,
                                                verify_mode=CERT_NONE)
                con = Sender(engine_config)
                for i in range(self.default_numbers_sendings):
                    con.send(tag=self.my_app, msg=self.test_msg)
                con.close()
            except Exception as error:
                return False
        else:
            return True

    def test_sender_as_handler(self):
        """
        Test that tries to check that Sender class can be used as a Handler
        and related logs are send to remote server
        """
        try:
            engine_config = SenderConfigSSL(address=(self.server, self.port),
                                            key=self.key, cert=self.cert,
                                            chain=self.chain,
                                            check_hostname=False,
                                            verify_mode=CERT_NONE)
            con = Sender.for_logging(config=engine_config, tag=self.my_app,
                                     level=TEST_FACILITY)
            logger = get_log(name="DevoLogger", handler=con,
                             level=TEST_FACILITY)
            print("Testing logger info")
            logger.info("Testing Sender inherit logging handler functio"
                        "nality... INFO - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger error")
            logger.error("Testing Sender inherit logging handler function"
                         "ality... ERROR - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger warning")
            logger.warning("Testing Sender inherit logging handler functio"
                           "nality... WARNING - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger debug")
            logger.debug("Testing Sender inherit logging handler functiona"
                         "lity... DEBUG - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger critical")
            logger.critical("Testing Sender inherit logging handler functio"
                            "nality... CRITICAL - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % str(error))

    def test_sender_with_default_logger(self):
        """
        Test that tries to check that Sender class can still use an internal
        logger and shows both local and remote
        traces
        """
        try:

            engine_config = SenderConfigSSL(address=(self.server, self.port),
                                            key=self.key, cert=self.cert,
                                            chain=self.chain,
                                            check_hostname=False,
                                            verify_mode=CERT_NONE)
            con = Sender.for_logging(config=engine_config, tag=self.my_app,
                                     level=TEST_FACILITY)
            # NOTE: this logger logging traces will be visible in console
            con.logger.info("Testing Sender default handler functionality in "
                            "local console... INFO - log")
            # NOTE: this logger logging traces will be visible in the remote
            # table
            con.info("Testing Sender default handler functionality in remote "
                     "table... INFO - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % str(error))

    def test_sender_as_handler_static(self):
        """
        Test that tries to check that Sender class can be used as a Handler
        through the static functions
        and related logs are send to remote server
        """
        try:
            engine_config = {"address": self.server, "port": self.port,
                             "key": self.key, "cert": self.cert,
                             "chain": self.chain, "check_hostname": False,
                             "verify_mode": CERT_NONE}

            con = Sender.for_logging(config=engine_config, tag=self.my_app,
                                     level=TEST_FACILITY)
            logger = get_log(name="DevoLogger2", handler=con,
                             level=TEST_FACILITY)

            print("Testing logger info")
            logger.info("Testing Sender static handler functionality... "
                        "INFO - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger error")
            logger.error("Testing Sender static logging handler "
                         "functionality... ERROR - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger warning")
            logger.warning("Testing Sender static logging handler "
                           "functionality... WARNING - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger debug")
            logger.debug("Testing Sender static logging handler "
                         "functionality... DEBUG - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            print("Testing logger critical")
            logger.critical("Testing Sender static logging handler "
                            "functionality... CRITICAL - log")
            data_received = con.socket.recv(5000)
            print(b"\n" + data_received)
            if len(data_received) == 0:
                raise Exception('Not msg sent!')

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % str(error))

    def test_config_files_path_standard_case(self):
        """
        Test that verifies that a correct path for the
        configuration file is detected.
        """

        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key,
                                        cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE,
                                        verify_config=False)

        result = engine_config.check_config_files_path()
        self.assertTrue(result)

    def test_config_files_path_incorrect_key(self):
        """
        Test that verifies that an incorrect path for the
        configuration raises an exception.
        """
        wrong_key = SenderConfigSSL(address=(self.server, self.port),
                                    key="Incorrect key",
                                    cert=self.cert,
                                    chain=self.chain,
                                    check_hostname=False,
                                    verify_mode=CERT_NONE,
                                    verify_config=False)

        wrong_key_message = "Error in the configuration, " + \
                            wrong_key.key + \
                            " is not a file or the path does not exist"

        with self.assertRaises(DevoSenderException) as result:
            wrong_key.check_config_files_path()

        self.assertEqual(wrong_key_message, str(result.exception))

    def test_config_files_path_incorrect_cert(self):

        wrong_cert = SenderConfigSSL(address=(self.server, self.port),
                                     key=self.key,
                                     cert="Incorrect cert",
                                     chain=self.chain,
                                     check_hostname=False,
                                     verify_mode=CERT_NONE,
                                     verify_config=False)

        wrong_cert_message = "Error in the configuration, " + \
                             wrong_cert.cert + \
                             " is not a file or the path does not exist"

        with self.assertRaises(DevoSenderException) as result:
            wrong_cert.check_config_files_path()

        self.assertEqual(wrong_cert_message, str(result.exception))

    def test_config_files_path_incorrect_chain(self):
        wrong_chain = SenderConfigSSL(address=(self.server, self.port),
                                      key=self.chain,
                                      cert=self.cert,
                                      chain="Incorrect chain",
                                      check_hostname=False,
                                      verify_mode=CERT_NONE,
                                      verify_config=False)
        wrong_chain_message = "Error in the configuration, " + \
                              wrong_chain.chain + \
                              " is not a file or the path does not exist"

        with self.assertRaises(DevoSenderException) as result:
            wrong_chain.check_config_files_path()

        self.assertEqual(wrong_chain_message, str(result.exception))

    def test_config_cert_key_standard_case(self):
        """
        Test that verifies that a compatible certificate
        and key are detected.
        """

        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key,
                                        cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE,
                                        verify_config=False)
        result = engine_config.check_config_certificate_key()
        self.assertTrue(result)

    def test_config_cert_key_incompatible_case(self):
        """
        Test that verifies that an incompatible
        certificate with a key raises an exception.
        """

        engine_config = SenderConfigSSL(
            address=(self.server, self.port),
            key=self.key,
            cert="{!s}/local_certs/keys/server/server_cert.pem".
            format(os.path.dirname(os.path.abspath(__file__))),
            chain=self.chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
            verify_config=False)

        with self.assertRaises(DevoSenderException) as result:
            engine_config.check_config_certificate_key()

        expected_exception = "Error in the configuration, the key: " + \
                             engine_config.key + \
                             " is not compatible with the cert: " +\
                             engine_config.cert

        self.assertIn(expected_exception, str(result.exception))

    def test_config_cert_chain_standard_case(self):
        """
        Test that verifies that a compatible certificate
        and chain are detected.
        """

        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key,
                                        cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE,
                                        verify_config=False)
        result = engine_config.check_config_certificate_chain()
        self.assertTrue(result)

    def test_config_cert_chain_incompatible_case(self):
        """
        Test that verifies that an incompatible
        certificate with a chain raises an exception.
        """

        engine_config = SenderConfigSSL(
            address=(self.server, self.port),
            key=self.key,
            cert=self.cert,
            chain="{!s}/local_certs/keys/server/server_cert.pem".
            format(os.path.dirname(os.path.abspath(__file__))),
            check_hostname=False,
            verify_mode=CERT_NONE,
            verify_config=False)

        with self.assertRaises(DevoSenderException) as result:
            engine_config.check_config_certificate_chain()

        expected_exception = "Error in config, " \
                             "the chain: " + engine_config.chain +\
                             " is not compatible with " \
                             "the certificate: " + engine_config.cert

        self.assertIn(expected_exception, str(result.exception))

    def test_config_cert_address_standard_case(self):
        """
        Test that verifies that a compatible certificate
        and address are detected.
        """
        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key,
                                        cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE,
                                        verify_config=False)
        chain = engine_config.fake_get_peer_cert_chain(self.chain)
        with mock.patch.object(
                SSL.Connection, 'get_peer_cert_chain',
                mock.MagicMock(return_value=chain)):
            result = engine_config.check_config_certificate_address()
            self.assertTrue(result)

    def test_config_cert_address_incompatible_address(self):
        """
        Test that verifies that an incompatible certificate
        and address raises an exception.
        """
        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key,
                                        cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE,
                                        verify_config=False)

        with self.assertRaises(DevoSenderException) as result:
            engine_config.check_config_certificate_address()

        expected_exception = "Error in config, " + \
                             "the certificate in the address: " + \
                             engine_config.address[0] +\
                             " is not compatible with: " +\
                             engine_config.chain

        self.assertIn(expected_exception, str(result.exception))

    def test_config_cert_address_incompatible_port(self):
        """
        Test that verifies that a wrong port raises an exception.
        """
        engine_config = SenderConfigSSL(
            address=("eu.elb.relay.logtrust.net", 442),
            key=self.key,
            cert=self.cert,
            chain=self.chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
            verify_config=False)

        with self.assertRaises(DevoSenderException) as result:
            engine_config.check_config_certificate_address()

        expected_exception = "Possible error in config, " \
                             "a timeout could be related " + \
                             "to an incorrect address/port: " + \
                             str(engine_config.address)

        self.assertIn(expected_exception, str(result.exception))

    def test_get_common_names(self):

        engine_config = SenderConfigSSL(
            address=("eu.elb.relay.logtrust.net", 442),
            key=self.key,
            cert=self.cert,
            chain=self.chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
            verify_config=False)
        cert_1 = engine_config.fake_get_peer_cert_chain(self.chain)
        cert_2 = engine_config.fake_get_peer_cert_chain(self.chain)
        subject = engine_config.get_common_names(cert_1, "get_subject")
        issuer = engine_config.get_common_names(cert_2, "get_issuer")

        self.assertTrue(issuer.issubset(subject))

    def fake_get_peer_cert_chain(self):
        engine_config = SenderConfigSSL(
            address=("eu.elb.relay.logtrust.net", 442),
            key=self.key,
            cert=self.cert,
            chain=self.chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
            verify_config=False)

        fake_chain_cert = \
            engine_config.fake_get_peer_cert_chain(self.chain)
        with open(self.chain, "rb") as chain_file:
            chain_certs = []
            for _ca in pem.parse(chain_file.read()):
                chain_certs.append(
                    crypto.load_certificate(
                        crypto.FILETYPE_PEM, str(_ca)))
        self.assertEqual(chain_certs, fake_chain_cert)
