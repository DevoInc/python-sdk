import unittest
import os
from devo.sender import Sender, SenderConfigTCP, SenderConfigSSL
from .local_server import create_ssl_server, create_tcp_server


class TestSender(unittest.TestCase):
    def setUp(self):
        self.server = os.getenv('DEVO_SENDER_SERVER',
                                "0.0.0.0")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 4443))

        self.tcp_server = os.getenv('DEVO_SENDER_self.tcp_server',
                                    "0.0.0.0")
        self.tcp_port = int(os.getenv('DEVO_SENDER_self.tcp_server', 4442))

        self.key = os.getenv('DEVO_SENDER_KEY', "client.key")
        self.cert = os.getenv('DEVO_SENDER_CERT', "client.crt")
        self.chain = os.getenv('DEVO_SENDER_CHAIN', "ca.crt")

        self.test_tcp = os.getenv('DEVO_TEST_TCP', "True")
        self.my_app = 'test.drop.devosender'
        self.my_date = 'my.date.test.sender'

        self.test_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                                  os.sep, "testfile_multiline.txt"))
        self.local_server = None

    def test_tcp_rt_send(self):
        if self.test_tcp == "True":
            self.local_server = create_tcp_server()
            engine_config = SenderConfigTCP(address=self.tcp_server,
                                            port=self.tcp_port)
            con = Sender(engine_config)
            for i in range(0, 100):
                con.send(tag=self.my_app, msg='Test TCP msg')
            con.close()
            self.local_server = None
        else:
            return True

    def test_ssl_rt_send(self):
        self.local_server = create_ssl_server()
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                        key=self.key, cert=self.cert,
                                        chain=self.chain)
        con = Sender(engine_config)
        for i in range(0, 100):
            con.send(tag=self.my_app, msg='Test SSL msg')
        con.close()
        self.local_server = None

    def test_multiline_send(self):
        self.local_server = create_ssl_server()
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                        key=self.key, cert=self.cert,
                                        chain=self.chain)
        con = Sender(engine_config)
        with open(self.test_file, 'r') as file:
            content = file.read()
        con.send(tag=self.my_app, msg=content, multiline=True)
        con.close()
        self.local_server = None

    def test_rt_send_no_certs(self):
        if self.test_tcp == "True":
            self.local_server = create_tcp_server()
            engine_config = SenderConfigSSL(address=self.tcp_server,
                                            port=self.tcp_port,
                                            certs_req=False)
            con = Sender(engine_config)
            for i in range(0, 100):
                con.send(tag=self.my_app, msg='Test RT msg')
            con.close()
            self.local_server = None
        else:
            return True


if __name__ == '__main__':
    unittest.main()
