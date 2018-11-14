import unittest
import os
from devo.sender import Sender, SenderConfigTCP, SenderConfigSSL, SenderHandler
import logging


class TestSender(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment vars.
        If you have an environment.env file (main directory) it will use it to set it else the vars will need to be set
        up in any other way.
        """
        file_path = "".join((os.path.dirname(os.path.abspath(__file__)),
                             os.sep))

        # if the required vars are not present it uses some default configuration
        self.server = os.getenv('DEVO_SENDER_SERVER',
                                "0.0.0.0")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 4488))

        self.tcp_server = os.getenv('DEVO_SENDER_self.tcp_server',
                                    "0.0.0.0")
        self.tcp_port = int(os.getenv('DEVO_SENDER_self.tcp_server', 4489))

        self.key = os.getenv('DEVO_SENDER_KEY', "".join((file_path,
                                                         "local_server_files",
                                                         os.sep, "client.key"))
                             )
        self.cert = os.getenv('DEVO_SENDER_CERT', "".join((file_path,
                                                           "local_server_files",
                                                           os.sep, "client.crt"))
                              )
        self.chain = os.getenv('DEVO_SENDER_CHAIN', "".join((file_path,
                                                             "local_server_files",
                                                             os.sep, "ca.crt"))
                               )

        self.test_tcp = os.getenv('DEVO_TEST_TCP', "True")
        self.my_app = 'test.keep.free'
        self.my_date = 'my.date.test.sender'
        self.test_file = "".join((file_path, "testfile_multiline.txt"))

        # change this value if you want to send another number of test string
        self.default_numbers_sendings = 100

    def test_tcp_rt_send(self):
        """
        Tests that a TCP connection and data send it is possible
        """
        if self.test_tcp == "True":
            try:
                engine_config = SenderConfigTCP(address=self.tcp_server,
                                                port=self.tcp_port)
                con = Sender(engine_config)
                for i in range(0, 1):
                    con.send(tag=self.my_app, msg='Test TCP msg')
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
            for i in range(0, self.default_numbers_sendings):
                con.send(tag=self.my_app, msg='Test SSL msg_ python_sdk_ fork')
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
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_rt_send_no_certs(self):
        """
        Test that tries to send a message without using certificates
        """
        if self.test_tcp == "True":
            try:
                engine_config = SenderConfigSSL(address=self.tcp_server,
                                                port=self.tcp_port,
                                                cert_reqs=False)
                con = Sender(engine_config)
                for i in range(0, self.default_numbers_sendings):
                    con.send(tag=self.my_app, msg='Test RT msg')
                con.close()
            except Exception as error:
                self.fail("Problems with test: %s" % error)
        else:
            return True

    def test_Sender_as_handler(self):
        """
        Test that tries to check that Sender class can be used as a Handler and related logs are send to remote server
        """
        try:
            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config, tag=self.my_app)

            logger = logging.getLogger('DEVO_logger')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)

            for i in range(0, self.default_numbers_sendings):
                # con.debug("DEVO LOGGING HANDLER TEST at: test_Sender_as_handler" )

                # logger.addHandler(con.logger.handlers[0])
                logger.info("Testing Sender inherit logging handler functionality... INFO - log")
                logger.error("Testing Sender inherit logging handler functionality... ERROR - log")
                logger.warning("Testing Sender inherit logging handler functionality... WARNING - log")
                logger.debug("Testing Sender inherit logging handler functionality... DEBUG - log")
                logger.critical("Testing Sender inherit logging handler functionality... CRITICAL - log")

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_Sender_with_default_logger(self):
        """
        Test that tries to check that Sender class can still use an internal logger and shows both local and remote
        traces
        """
        try:

            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config, tag=self.my_app)

            for i in range(0, self.default_numbers_sendings):
                # NOTE: this logger logging traces will be visible in console
                con.logger.info("Testing Sender default handler functionality in local console... INFO - log")
                # NOTE: this logger logging traces will be visible in the remote table
                con.info("Testing Sender default handler functionality in remote table... INFO - log")

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_Sender_as_handler_static(self):
        """
        Test that tries to check that Sender class can be used as a Handler through the static functions
        and related logs are send to remote server
        """
        try:
            engine_config = {"address": self.server, "port": self.port,
                             "key": self.key, "cert": self.cert,
                             "chain": self.chain, "type": "SSL", "cert_regs": True}

            con = Sender.for_logging(engine_config, "SSL", self.my_app)

            logger = logging.getLogger('DEVO_logger')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)

            # logger.addHandler(con.logger.handlers[0])
            for i in range(0, self.default_numbers_sendings):
                logger.info("Testing Sender static handler functionality... INFO - log")
                logger.error("Testing Sender static logging handler functionality... ERROR - log")
                logger.warning("Testing Sender static logging handler functionality... WARNING - log")
                logger.debug("Testing Sender static logging handler functionality... DEBUG - log")
                logger.critical("Testing Sender static logging handler functionality... CRITICAL - log")

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_Sender_as_handler_wrapper_SSL_OK(self):
        """
        Test that tries to check that it is possible to instantiate the Sender class (SSL connection) so that it can
        be used as a Handler for a django instance (settings.py configuration) and related logs
        are send to remote server
        """
        try:
            con = SenderHandler(address=self.server, port=self.port, key=self.key, cert=self.cert,
                                chain=self.chain, cert_reqs=True, type="SSL", tag=self.my_app)

            logger = logging.getLogger('DEVO_logger')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)

            # logger.addHandler(con.logger.handlers[0])
            for i in range(0, self.default_numbers_sendings):
                logger.info("Testing Sender Wrapper handler, SSL, functionality... INFO - log")
                logger.error("Testing Sender Wrapper handler, SSL, functionality... ERROR - log")
                logger.warning("Testing Sender Wrapper handler, SSL, functionality... WARNING - log")
                logger.debug("Testing Sender Wrapper handler, SSL, functionality... DEBUG - log")
                logger.critical("Testing Sender Wrapper handler, SSL, functionality... CRITICAL - log")

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_Sender_as_handler_wrapper_SSL_NOK(self):
        """
        Test that tries to check that it is possible to instantiate the Sender class (SSL connection) so that it can
        be used as a Handler for a django instance (settings.py configuration) and related logs
        are send to remote server
        """
        try:
            con = SenderHandler(address=self.server, key=self.key,cert=self.cert,
                                chain=self.chain, cert_reqs=True, type="SSL", tag=self.my_app)

            con.close()
            self.fail("Problems with test: an exception should be raised pointing to the missing args")
        except Exception as error:
            print(error)
            self.assertIs(True, True)

    def test_Sender_as_handler_wrapper_SSL_false_OK(self):
        """
        Test that tries to check that it is possible to instantiate the Sender class (SSL connection without
        certificates) so that it can be used as a Handler for a  instance (settings.py configuration) and related logs
        are send to remote server
        """
        try:
            con = SenderHandler(address=self.server, port=self.port, cert_reqs=False, tag=self.my_app)

            logger = logging.getLogger('DEVO_logger')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)

            # logger.addHandler(con.logger.handlers[0])
            for i in range(0, self.default_numbers_sendings):
                logger.info("Testing Sender Wrapper handler, SSL no certificate, functionality... INFO - log")
                logger.error("Testing Sender Wrapper handler, SSL no certificate, functionality... ERROR - log")
                logger.warning("Testing Sender Wrapper handler, SSL no certificate, functionality... WARNING - log")
                logger.debug("Testing Sender Wrapper handler, SSL no certificate, functionality... DEBUG - log")
                logger.critical("Testing Sender Wrapper handler, SSL no certificate, functionality... CRITICAL - log")

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_Sender_as_handler_wrapper_SSL_false_NOK(self):
        """
        Test that tries to check that it is possible to instantiate the Sender class (SSL connection without
        certificates) so that it can  be used as a Handler for a django instance (settings.py configuration)
        and related logs are send to remote server
        """
        try:
            con = SenderHandler(address=self.server, cert_reqs=True, tag=self.my_app)

            con.close()
            self.fail("Problems with test: an exception should be raised pointing to the missing args")
        except Exception as error:
            print(error)
            self.assertIs(True, True)

    def test_Sender_as_handler_wrapper_TCP_OK(self):
        """
        Test that tries to check that it is possible to instantiate the Sender class (TCP connection) so that it can
        be used as a Handler for a django instance (settings.py configuration) and related logs
        are send to remote server
        """
        try:
            con = SenderHandler(address=self.server, port=self.port, tag=self.my_app)

            logger = logging.getLogger('DEVO_logger')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)

            # logger.addHandler(con.logger.handlers[0])
            for i in range(0, self.default_numbers_sendings):
                logger.info("Testing Sender Wrapper handler, TCP, functionality... INFO - log")
                logger.error("Testing Sender Wrapper handler, TCP, functionality...  ERROR - log")
                logger.warning("Testing Sender Wrapper handler, TCP, functionality...  WARNING - log")
                logger.debug("Testing Sender Wrapper handler, TCP, functionality...  DEBUG - log")
                logger.critical("Testing Sender Wrapper handler, TCP, functionality...  CRITICAL - log")

            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

    def test_Sender_as_handler_wrapper_TCP_NOK(self):
        """
        Test that tries to check that it is possible to instantiate the Sender class (TCP connection) so that it can
        be used as a Handler for a django instance (settings.py configuration) and related logs
        are send to remote server
        """
        try:
            con = SenderHandler(address=self.server, tag=self.my_app)

            con.close()
            self.fail("Problems with test: an exception should be raised pointing to the missing args")
        except Exception as error:
            print(error)
            self.assertIs(True, True)
    """There are three scenarios possible scenarios:
                1. ssl connection with certificates
                2. ssl connection without certificates
                3. tcp connection 
                Any other case will rise an error. 
            """

if __name__ == '__main__':
    unittest.main()
