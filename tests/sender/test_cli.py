import os
import socket
import tempfile
import unittest

from click.testing import CliRunner

from devo.common import Configuration
from devo.common.generic.configuration import ConfigurationException
from devo.sender import DevoSenderException
from devo.sender.scripts.sender_cli import data, lookup

from .load_certs import CLIENT_CERT, CLIENT_CHAIN, CLIENT_KEY


class TestSender(unittest.TestCase):
    def setUp(self):
        self.local_address = os.getenv("DEVO_SENDER_SERVER", "127.0.0.1")
        self.local_port = int(os.getenv("DEVO_SENDER_PORT", 4488))
        self.tcp_address = os.getenv("DEVO_SENDER_TCP_SERVER", "127.0.0.1")
        self.tcp_port = int(os.getenv("DEVO_SENDER_TCP_PORT", 4489))

        self.remote_address = os.getenv(
            "DEVO_REMOTE_SENDER_SERVER", "collector-us.devo.io"
        )
        self.remote_port = int(os.getenv("DEVO_REMOTE_SENDER_PORT", 443))

        self.key = os.getenv("DEVO_SENDER_KEY", CLIENT_KEY)
        self.cert = os.getenv("DEVO_SENDER_CERT", CLIENT_CERT)
        self.chain = os.getenv("DEVO_SENDER_CHAIN", CLIENT_CHAIN)

        self.local_key = CLIENT_KEY
        self.test_tcp = os.getenv("DEVO_TEST_TCP", "True")
        self.my_app = "test.drop.free"
        self.my_bapp = b"test.drop.free"
        self.my_date = "my.date.test.sender"
        self.test_file = "".join(
            (
                os.path.dirname(os.path.abspath(__file__)),
                os.sep,
                "testfile_multiline.txt",
            )
        )

        self.lookup_file = "".join(
            (
                os.path.dirname(os.path.abspath(__file__)),
                os.sep,
                "testfile_lookup_with_quotes.csv",
            )
        )
        self.lookup_name = "TEST_LOOKUP"

        self.test_msg = "Test send msg\n"
        self.localhost = socket.gethostname()
        # change this value if you want to send another number of test string
        self.default_numbers_sendings = 10

        configuration = Configuration()
        configuration.set(
            "sender",
            {
                "key": self.key,
                "cert": self.cert,
                "chain": self.chain,
                "address": self.local_address,
                "port": self.local_port,
                "verify_mode": 0,
                "check_hostname": False,
            },
        )

        self.config_path = os.path.join(
            tempfile.gettempdir(), "devo_api_tests_config.json"
        )
        configuration.save(path=self.config_path)

        self.bad_json_config_path = "./common/bad_json_config.json"
        self.bad_yaml_config_path = "./common/bad_yaml_config.yaml"

    def test_cli_args(self):
        runner = CliRunner()
        result = runner.invoke(data, [])
        self.assertIn("No address", result.stdout)

    def test_cli_bad_address(self):
        runner = CliRunner()
        result = runner.invoke(
            data, ["--debug", "--type", "TCP", "--address", self.local_address + "asd"]
        )
        self.assertIsInstance(result.exception, DevoSenderException)
        self.assertIn("TCP conn establishment socket error", result.stdout)

    def test_cli_bad_certs(self):
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--address",
                "collector-us.devo.io",
                "--port",
                "443",
                "--key",
                self.local_key,
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--verify_mode",
                1,
                "--check_hostname",
                True,
            ],
        )
        self.assertIsInstance(result.exception, DevoSenderException)
        self.assertIn("Error in the configuration", result.exception.args[0])

    def test_cli_bad_certs_no_verify_on(self):
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--address",
                "collector-us.devo.io",
                "--port",
                "443",
                "--key",
                self.local_key,
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--verify_mode",
                1,
                "--check_hostname",
                True,
                "--no-verify-certificates",
            ],
        )
        self.assertIsInstance(result.exception, DevoSenderException)
        self.assertIn("SSL conn establishment socket error", result.exception.args[0])

    def test_cli_notfound_certs(self):
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--address",
                "collector-us.devo.io",
                "--port",
                "443",
                "--key",
                "not_a_folder/not_a_file",
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--verify_mode",
                1,
                "--check_hostname",
                True,
            ],
        )
        self.assertIsInstance(result.exception, SystemExit)
        self.assertIn(
            "Error: Invalid value for '--key': Path "
            "'not_a_folder/not_a_file' does not exist.",
            result.output,
        )

    def test_cli_normal_send_without_certificates_checking(self):
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--address",
                self.local_address,
                "--port",
                self.local_port,
                "--key",
                self.key,
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--tag",
                self.my_app,
                "--verify_mode",
                0,
                "--check_hostname",
                False,
                "--line",
                "Test line",
                "--no-verify-certificates",
            ],
        )

        self.assertIsNone(result.exception)
        self.assertGreater(int(result.output.split("Sended: ")[-1]), 0)

    def test_cli_normal_send_with_certificates_checking(self):
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--address",
                self.remote_address,
                "--port",
                self.remote_port,
                "--key",
                self.key,
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--tag",
                self.my_app,
                "--verify_mode",
                0,
                "--check_hostname",
                False,
                "--line",
                "Test line",
            ],
        )

        self.assertIsNone(result.exception)
        self.assertGreater(int(result.output.split("Sended: ")[-1]), 0)

    def test_cli_normal_send_multiline_with_certificates_checking(self):
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--address",
                self.remote_address,
                "--port",
                self.remote_port,
                "--key",
                self.key,
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--tag",
                self.my_app,
                "--verify_mode",
                0,
                "--check_hostname",
                False,
                "--multiline",
                "--file",
                self.test_file,
            ],
        )

        self.assertIsNone(result.exception)
        self.assertGreater(int(result.output.split("Sended: ")[-1]), 0)

    def test_cli_with_config_file(self):
        if self.config_path:
            runner = CliRunner()
            result = runner.invoke(
                data,
                ["--debug", "--config", self.config_path, "--no-verify-certificates"],
            )

            self.assertIsNone(result.exception)
            self.assertGreater(int(result.output.split("Sended: ")[-1]), 0)

    def test_cli_with_bad_json_config_file(self):
        if self.config_path:
            runner = CliRunner()
            result = runner.invoke(
                data,
                [
                    "--debug",
                    "--config",
                    self.bad_json_config_path,
                    "--no-verify-certificates",
                ],
            )

            self.assertIsNotNone(result.exception)
            self.assertIsInstance(result.exception, ConfigurationException)
            self.assertEquals(
                "Configuration file seems not to be a valid JSON file",
                result.exception.args[0],
            )

    def test_cli_with_bad_yaml_config_file(self):
        if self.config_path:
            runner = CliRunner()
            result = runner.invoke(
                data,
                [
                    "--debug",
                    "--config",
                    self.bad_yaml_config_path,
                    "--no-verify-certificates",
                ],
            )

            self.assertIsNotNone(result.exception)
            self.assertIsInstance(result.exception, ConfigurationException)
            self.assertEquals(
                "Configuration file seems not to be a valid YAML file",
                result.exception.args[0],
            )

    def test_cli_escape_quotes(self):
        runner = CliRunner()
        result = runner.invoke(
            lookup,
            [
                "--debug",
                "--address",
                self.local_address,
                "--port",
                self.local_port,
                "--key",
                self.key,
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--verify_mode",
                0,
                "--check_hostname",
                False,
                "-n",
                self.lookup_name,
                "-ac",
                "FULL",
                "-f",
                self.lookup_file,
                "-lk",
                "KEY",
                "-eq",
                "--no-verify-certificates",
            ],
        )

        self.assertIsNone(result.exception)
        self.assertEquals(result.exit_code, 0)

    def test_cli_not_escape_quotes(self):
        runner = CliRunner()
        result = runner.invoke(
            lookup,
            [
                "--debug",
                "--address",
                self.local_address,
                "--port",
                self.local_port,
                "--key",
                self.key,
                "--cert",
                self.cert,
                "--chain",
                self.chain,
                "--verify_mode",
                0,
                "--check_hostname",
                False,
                "-n",
                self.lookup_name,
                "-ac",
                "FULL",
                "-f",
                self.lookup_file,
                "-lk",
                "KEY",
                "--no-verify-certificates",
            ],
        )

        self.assertIsNotNone(result.exception)
        self.assertEquals(result.exit_code, 64)


if __name__ == "__main__":
    unittest.main()
