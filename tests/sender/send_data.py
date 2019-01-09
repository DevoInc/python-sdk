import unittest
import logging
import socket
import sys
from devo.sender import Sender, SenderConfigTCP, SenderConfigSSL
from .load_certs import *

PY3 = sys.version_info[0] > 2


class TestSender(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment vars.
        If you have an environment.env file (main directory) it will use it
        to set it else the vars will need to be set
        up in any other way.
        """
        self.server = os.getenv('DEVO_SENDER_SERVER', "0.0.0.0")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 4488))
        self.tcp_server = os.getenv('DEVO_SENDER_TCP_SERVER', "0.0.0.0")
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
        if self.test_tcp == "True" and PY3:
            try:
                engine_config = SenderConfigTCP(address=self.tcp_server,
                                                port=self.tcp_port)
                con = Sender(engine_config)
                for i in range(self.default_numbers_sendings):
                    con.send(tag=self.my_app, msg=self.test_msg)
                    if len(con.socket.recv(5000)) == 0:
                        raise Exception('Not msg sent!')
                con.close()
            except Exception as error:
                self.fail("Problems with test: %s" % error)
        else:
            return True

    def test_ssl_rt_send(self):
        """
        Test that tries to send a message through a ssl connection
        """
        try:
            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config)
            for i in range(self.default_numbers_sendings):
                con.send(tag=self.my_app, msg=self.test_msg)
                if len(con.socket.recv(5000)) == 0:
                    raise Exception('Not msg sent!')
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_ssl_zip_send(self):
        """
        Test that tries to send a message through a ssl connection
        """
        try:
            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config, sockettimeout=15)
            for i in range(self.default_numbers_sendings):
                con.send(tag=self.my_bapp, msg=self.test_msg.encode("utf-8")
                         , zip=True)
                con.flush_buffer()
                if len(con.socket.recv(1000)) == 0:
                    raise Exception('Not msg sent!')
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_multiline_send(self):
        """
        Test that tries to send a multiple line message through a ssl connection
        """
        try:
            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config)
            with open(self.test_file, 'r') as file:
                content = file.read()

            con.send(tag=self.my_app, msg=content, multiline=True)
            con.flush_buffer()

            if len(con.socket.recv(5000)) == 0:
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
                engine_config = SenderConfigSSL(address=self.server,
                                                port=self.port,
                                                cert_reqs=False)
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
            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config, tag=self.my_app)

            logger = logging.getLogger('DEVO_logger')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s'
                                          '|%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)

            logger.info("Testing Sender inherit logging handler functio"
                        "nality... INFO - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.error("Testing Sender inherit logging handler function"
                         "ality... ERROR - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.warning("Testing Sender inherit logging handler functio"
                           "nality... WARNING - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.debug("Testing Sender inherit logging handler functiona"
                         "lity... DEBUG - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.critical("Testing Sender inherit logging handler functio"
                            "nality... CRITICAL - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_sender_with_default_logger(self):
        """
        Test that tries to check that Sender class can still use an internal
        logger and shows both local and remote
        traces
        """
        try:

            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config, tag=self.my_app)

            # NOTE: this logger logging traces will be visible in console
            con.logger.info("Testing Sender default handler functionality in "
                            "local console... INFO - log")
            # NOTE: this logger logging traces will be visible in the remote
            # table
            con.info("Testing Sender default handler functionality in remote "
                     "table... INFO - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_sender_as_handler_static(self):
        """
        Test that tries to check that Sender class can be used as a Handler
        through the static functions
        and related logs are send to remote server
        """
        try:
            engine_config = {"address": self.server, "port": self.port,
                             "key": self.key, "cert": self.cert,
                             "chain": self.chain, "type": "SSL", "cert_regs": True}
            con = Sender.for_logging(engine_config, "SSL", self.my_app)
            logger = logging.getLogger('DEVO_logger_static')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|'
                                          '%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)

            logger.info("Testing Sender static handler functionality... "
                        "INFO - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.error("Testing Sender static logging handler "
                         "functionality... ERROR - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.warning("Testing Sender static logging handler "
                           "functionality... WARNING - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.debug("Testing Sender static logging handler "
                         "functionality... DEBUG - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            logger.critical("Testing Sender static logging handler "
                            "functionality... CRITICAL - log")
            if len(con.socket.recv(5000)) == 0:
                raise Exception('Not msg sent!')

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)
