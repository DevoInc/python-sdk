import unittest
import os
from devo.sender import Sender, SenderConfigTCP, SenderConfigSSL


class TestSender(unittest.TestCase):
    def setUp(self):
        file_path = "".join((os.path.dirname(os.path.abspath(__file__)),
                                  os.sep))

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
        self.my_app = 'test.drop.devosender'
        self.my_date = 'my.date.test.sender'

        self.test_file = "".join((file_path, "testfile_multiline.txt"))


    def test_tcp_rt_send(self):
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
        try:
            engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                            key=self.key, cert=self.cert,
                                            chain=self.chain)
            con = Sender(engine_config)
            for i in range(0, 100):
                con.send(tag=self.my_app, msg='Test SSL msg')
            con.close()
        except Exception as error:
            self.fail("Problems with test: %s" % error)


    def test_multiline_send(self):
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
        if self.test_tcp == "True":
            try:
                engine_config = SenderConfigSSL(address=self.tcp_server,
                                                port=self.tcp_port,
                                                certs_req=False)
                con = Sender(engine_config)
                for i in range(0, 100):
                    con.send(tag=self.my_app, msg='Test RT msg')
                con.close()
            except Exception as error:
                self.fail("Problems with test: %s" % error)
        else:
            return True


if __name__ == '__main__':
    unittest.main()
