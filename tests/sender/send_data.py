import unittest,threading,os,time
from devo.sender import Sender, SenderConfigTCP, SenderConfigSSL
from devo.common import loadenv
from mock_server import start_server,file_path,ip_server,port_server,tcp_server,tcp_port
import logging


class TestSender(unittest.TestCase):
    def setUp(self):

        # if the required vars are not present it uses some default configuration
        self.server = ip_server
        self.port = port_server
        self.tcp_server = tcp_server
        self.tcp_port = tcp_port

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
        self.my_app = 'test.drop.free'
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
            #for i in range(0, self.default_numbers_sendings):
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
        try:
            engine_config = SenderConfigSSL(address=self.server,
                                            port=self.port,
                                            cert_reqs=False)
            con = Sender(engine_config)
            for i in range(0, self.default_numbers_sendings):
                con.send(tag=self.my_app, msg='Test RT msg')
            con.close()
            self.fail("Problems with test. Its possible send data without using certificates")
        except Exception as error:
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
            logger = logging.getLogger('DEVO_logger_static')
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
            con.setFormatter(formatter)
            con.setLevel(logging.DEBUG)
            logger.addHandler(con)
            for i in range(0, self.default_numbers_sendings):
                logger.info("Testing Sender static handler functionality... INFO - log")
                logger.error("Testing Sender static logging handler functionality... ERROR - log")
                logger.warning("Testing Sender static logging handler functionality... WARNING - log")
                logger.debug("Testing Sender static logging handler functionality... DEBUG - log")
                logger.critical("Testing Sender static logging handler functionality... CRITICAL - log")
            
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)

if __name__ == '__main__':
    start_server()  #launch the mock server    
    unittest.main() #execute tests
