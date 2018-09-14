import unittest
import os
from devo.sender import Sender, SenderConfigTCP, SenderConfigSSL


class TestSender(unittest.TestCase):
    def setUp(self):

        self.server = os.getenv('DEVO_SENDER_SERVER',
                                "eu.elb.relay.logtrust.net")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 443))

        self.tcp_server = os.getenv('DEVO_SENDER_self.tcp_server',
                                         "eu.elb.relay.logtrust.net")
        self.tcp_port = int(os.getenv('DEVO_SENDER_self.tcp_server', 1514))

        self.key = os.getenv('DEVO_SENDER_KEY', None)
        self.cert = os.getenv('DEVO_SENDER_CERT', None)
        self.chain = os.getenv('DEVO_SENDER_CHAIN', None)

        self.test_tcp = os.getenv('DEVO_TEST_TCP', False)
        self.my_app = 'test.drop.devosender'
        self.my_date = 'my.date.test.sender'

        self.testfile_lookup = "%s%stestfile_lookup.csv" % (os.path.dirname(os.path.abspath(__file__)), os.sep)
        self.testfile_multiline = "%s%stestfile_multiline.txt" % (os.path.dirname(os.path.abspath(__file__)), os.sep)

    def test_tcp_rt_send(self):
        if self.test_tcp == "True":
            engine_config = SenderConfigTCP(address=self.tcp_server, port=self.tcp_port)
            con = Sender(engine_config)
            for i in range(0, 100):
                con.send(tag=self.my_app, msg='Test TCP msg')
        else:
            return True

    def test_ssl_rt_send(self):
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                          key=self.key, cert=self.cert,
                                          chain=self.chain)
        con = Sender(engine_config)
        for i in range(0, 100):
            con.send(tag=self.my_app, msg='Test SSL msg')

    def test_multiline_send(self):
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                          key=self.key, cert=self.cert,
                                          chain=self.chain)
        con = Sender(engine_config)
        with open(self.testfile_multiline, 'r') as file:
            content = file.read()
        con.send(tag=self.my_app, msg=content, multiline=True)

    def test_rt_send_no_certs(self):
        if self.test_tcp == "True":
            engine_config = SenderConfigSSL(address=self.tcp_server,
                                            port=self.tcp_port,
                                            certs_req=False)
            con = Sender(engine_config)
            for i in range(0, 100):
                con.send(tag=self.my_app, msg='Test RT msg')
        else:
            return True


if __name__ == '__main__':
    unittest.main()
