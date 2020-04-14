import unittest
import socket
from click.testing import CliRunner
from devo.common import Configuration
from devo.sender.scripts.sender_cli import data
from devo.sender import DevoSenderException

try:
    from .load_certs import *
except ImportError:
    from load_certs import *


class TestSender(unittest.TestCase):
    def setUp(self):
        self.address = os.getenv('DEVO_SENDER_SERVER', "127.0.0.1")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 4488))
        self.tcp_address = os.getenv('DEVO_SENDER_TCP_SERVER', "127.0.0.1")
        self.tcp_port = int(os.getenv('DEVO_SENDER_TCP_PORT', 4489))

        self.key = os.getenv('DEVO_SENDER_KEY', CLIENT_KEY)
        self.cert = os.getenv('DEVO_SENDER_CERT', CLIENT_CERT)
        self.chain = os.getenv('DEVO_SENDER_CHAIN', CLIENT_CHAIN)

        self.local_key = os.getenv(CLIENT_KEY)
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

        configuration = Configuration()
        configuration.set("sender", {
            "key": self.key, "cert": self.cert, "chain": self.chain,
            "address": self.address, "port": self.port,
            "verify_mode": 0, "check_hostname": False
        })

        self.config_path = "/tmp/devo_sender_tests_config.json"
        configuration.save(path=self.config_path)

    def test_sender_args(self):
        runner = CliRunner()
        result = runner.invoke(data, [])
        self.assertIn('No address', result.stdout)

    def test_bad_address(self):
        runner = CliRunner()
        result = runner.invoke(data, ["--debug",
                                      "--address", self.address + "asd"])

        self.assertIsInstance(result.exception, DevoSenderException)
        self.assertIn("Name or service not known",
                         result.exception.args[0])

    def test_bad_certs(self):
        runner = CliRunner()
        result = runner.invoke(data, ["--debug",
                                       "--address",
                                       "collector-us.devo.io",
                                       "--port", "443",
                                       "--key", self.local_key,
                                       "--cert", self.cert,
                                       "--chain", self.chain,
                                      "--verify_mode", 0,
                                      '--check_hostname', False])
        self.assertIsInstance(result.exception, DevoSenderException)
        self.assertIn("SSL conn establishment socket error",
                      result.exception.args[0])

    def test_normal_send(self):
        runner = CliRunner()
        result = runner.invoke(data, ["--debug",
                                      "--address", self.address,
                                      "--port", self.port,
                                      "--key", self.key,
                                      "--cert", self.cert,
                                      "--chain", self.chain,
                                      "--tag", self.my_app,
                                      "--verify_mode", 0,
                                      '--check_hostname', False,
                                      "--line", "Test line"])

        self.assertIsNone(result.exception)
        self.assertGreater(int(result.output.split("Sended: ")[-1]), 0)

    def test_with_config_file(self):
        if self.config_path:
            runner = CliRunner()
            result = runner.invoke(data, ["--debug",
                                          "--config", self.config_path])

            self.assertIsNone(result.exception)
            self.assertGreater(int(result.output.split("Sended: ")[-1]), 0)


if __name__ == '__main__':
    unittest.main()
