import os
import socket
import tempfile

import pytest
from click.testing import CliRunner
from devo.common import Configuration
from devo.common.generic.configuration import ConfigurationException
from devo.common.loadenv.load_env import load_env_file
from devo.sender import DevoSenderException
from devo.sender.scripts.sender_cli import data, lookup

from .local_servers import (SSLServer, TCPServer, _find_available_port,
                            _wait_for_ready_server)

# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


@pytest.fixture(scope="module", autouse=True)
def setup():

    class Fixture:
        pass

    setup = Fixture()

    # Server configuration
    # ----------------------------------------
    setup.ssl_address = os.getenv("DEVO_SENDER_SERVER", "127.0.0.1")
    setup.ssl_port = int(os.getenv("DEVO_SENDER_PORT", 4488))
    setup.tcp_address = os.getenv("DEVO_SENDER_TCP_SERVER", "127.0.0.1")
    setup.tcp_port = int(os.getenv("DEVO_SENDER_TCP_PORT", 4489))
    setup.remote_address = os.getenv("DEVO_REMOTE_SENDER_SERVER", "collector-us.devo.io")
    setup.remote_port = int(os.getenv("DEVO_REMOTE_SENDER_PORT", 443))

    # Resources configuration
    # ----------------------------------------
    setup.res_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "resources"
    setup.my_app = "test.drop.free"
    setup.my_bapp = b"test.drop.free"
    setup.my_date = "my.date.test.sender"
    setup.test_file = setup.res_path + os.sep + "testfile_multiline.txt"
    setup.lookup_file = setup.res_path + os.sep + "testfile_lookup_with_quotes.csv"
    setup.lookup_name = "TEST_LOOKUP"
    setup.test_msg = "Test send msg\n"
    setup.localhost = socket.gethostname()
    setup.default_numbers_sendings = 10  # change this value if you want

    # Certificates configuration - LOCAL SERVER
    # ----------------------------------------
    setup.certs_path = setup.res_path + os.sep + "local_certs" + os.sep + "keys"
    setup.server_key = os.getenv(
        "DEVO_SENDER_SERVER_KEY", f"{setup.certs_path}/server/private/server_key.pem"
    )
    setup.server_cert = os.getenv(
        "DEVO_SENDER_SERVER_CRT", f"{setup.certs_path}/server/server_cert.pem"
    )
    setup.chain = os.getenv("DEVO_SENDER_SERVER_CHAIN", f"{setup.certs_path}/ca/ca_cert.pem")
    setup.test_tcp = os.getenv("DEVO_TEST_TCP", "True")
    setup.configuration = Configuration()
    setup.configuration.set(
        "sender",
        {
            "key": setup.server_key,
            "cert": setup.server_cert,
            "chain": setup.chain,
            "address": setup.ssl_address,
            "port": setup.ssl_port,
            "verify_mode": 0,
            "check_hostname": False,
        },
    )

    # Certificates configuration - REMOTE SERVER
    # ----------------------------------------
    setup.key = os.getenv("DEVO_SENDER_KEY", f"{setup.res_path}/certs/us/devo_services.key")
    setup.cert = os.getenv("DEVO_SENDER_CRT", f"{setup.res_path}/certs/us/devo_services.crt")
    setup.ca = os.getenv("DEVO_SENDER_CHAIN", f"{setup.res_path}/certs/us/chain.crt")

    # Configuration files
    # ----------------------------------------
    setup.config_path = os.path.join(tempfile.gettempdir(), "devo_api_tests_config.json")
    setup.configuration.save(path=setup.config_path)

    # Common resources
    # ----------------------------------------
    setup.common_path = "".join(
        [
            os.path.dirname(os.path.abspath(__file__)),
            os.sep,
            "resources",
        ]
    )

    setup.bad_json_config_path = setup.common_path + os.sep + "bad_json_config.json"
    setup.bad_yaml_config_path = setup.common_path + os.sep + "bad_yaml_config.yaml"

    setup.ssl_port = _find_available_port(setup.ssl_address, setup.ssl_port)
    local_ssl_server = SSLServer(
        setup.ssl_address, setup.ssl_port, setup.server_cert, setup.server_key
    )

    setup.tcp_port = _find_available_port(setup.ssl_address, setup.ssl_port)
    local_tcp_server = TCPServer(setup.tcp_address, setup.tcp_port)

    _wait_for_ready_server(local_ssl_server.ip, local_ssl_server.port)

    yield setup

    local_ssl_server.close_server()
    local_tcp_server.close_server()


# @pytest.fixture(scope="module", autouse=True)
# def start_https_server(setup):
#     setup.ssl_port = _find_available_port(setup.ssl_address, setup.ssl_port)
#     httpd = http.server.ThreadingHTTPServer(
#         (setup.ssl_address, setup.ssl_port), http.server.SimpleHTTPRequestHandler
#     )
#     httpd.socket = ssl.wrap_socket(
#         httpd.socket,
#         server_side=True,
#         certfile=setup.server_cert,
#         keyfile=setup.server_key,
#         ssl_version=ssl.PROTOCOL_TLS,
#     )

#     # Start the server in a new thread
#     server_thread = threading.Thread(target=httpd.serve_forever)
#     server_thread.start()
#     _wait_for_ready_server(setup.ssl_address, setup.ssl_port)

#     yield  # This is where the testing happens

#     # After the tests, shut down the server
#     httpd.shutdown()
#     server_thread.join()

# @pytest.fixture(scope="module", autouse=True)
# def mock_ssl_server(setup):

#     class MockSSLHandler(http.server.SimpleHTTPRequestHandler):

#         def do_GET(self):
#             # Print the received GET request
#             print(f"Received GET request: {self.path}")

#             # Customize the response as needed
#             content_length = int(self.headers['Content-Length'])
#             # count = self.headers['Content-Length'] if self.headers['Content-Length'] else 0
#             self.send_response(200)
#             self.end_headers()
#             message = self.rfile.read(content_length).decode('utf-8')
#             # message = self.rfile.read(count).decode('utf-8')
#             print(message)
#             self.wfile.write(message.encode('utf-8'))

#         def do_POST(self):
#             # Read the content length
#             content_length = int(self.headers['Content-Length'])
#             # count = self.headers['Content-Length'] if self.headers['Content-Length'] else 0

#             # Read the message from the request
#             message = self.rfile.read(content_length).decode('utf-8')
#             # message = self.rfile.read(count).decode('utf-8')

#             # Print the received POST request and message
#             print(f"Received POST request: {self.path}")
#             print(message)

#             # Respond with a success message
#             self.send_response(200)
#             self.end_headers()
#             # self.wfile.write(f"Received message: {message}".encode('utf-8'))
#             self.wfile.write(message.encode('utf-8'))

#     # Set up SSL context with provided certificate and key
#     # certfile = request.config.getoption("--certfile")
#     # keyfile = request.config.getoption("--keyfile")
#     context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#     context.load_cert_chain(setup.server_cert, setup.server_key)

#     # Set up and start the SSL server
#     server_address = (setup.ssl_address, setup.ssl_port)
#     mock_server = http.server.ThreadingHTTPServer(server_address,
#                                                   MockSSLHandler)
#     # mock_server = http.server.HTTPServer(server_address, MockSSLHandler)
#     mock_server.socket = context.wrap_socket(mock_server.socket,
#                                              server_side=True)

#     # Start the server in a separate thread
#     server_thread = threading.Thread(target=mock_server.serve_forever)
#     server_thread.start()
#     _wait_for_ready_server(setup.ssl_address, setup.ssl_port)

#     yield mock_server

#     # Stop the server when the tests are done
#     mock_server.shutdown()
#     server_thread.join()


def test_cli_args():
    runner = CliRunner()
    result = runner.invoke(data, [])
    assert "No address" in result.stdout


def test_cli_bad_address(setup):
    runner = CliRunner()
    result = runner.invoke(
        data, ["--debug", "--type", "TCP", "--address", setup.ssl_address + "asd"]
    )
    assert isinstance(result.exception, DevoSenderException)
    assert "TCP conn establishment socket error" in result.stdout


def test_cli_bad_certs(setup):
    runner = CliRunner()
    result = runner.invoke(
        data,
        [
            "--debug",
            "--address",
            setup.remote_address,
            "--port",
            "443",
            "--key",
            setup.server_key,  # Not matching the remote cert
            "--cert",
            setup.cert,
            "--chain",
            setup.ca,
            "--verify_mode",
            1,
            "--check_hostname",
            True,
        ],
    )
    assert isinstance(result.exception, DevoSenderException)
    assert "Error in the configuration" in result.exception.args[0]


def test_cli_bad_certs_no_verify_on(setup):
    runner = CliRunner()
    result = runner.invoke(
        data,
        [
            "--debug",
            "--address",
            setup.remote_address,
            "--port",
            "443",
            "--key",
            setup.server_key,  # Not matching the remote cert
            "--cert",
            setup.cert,
            "--chain",
            setup.ca,
            "--verify_mode",
            1,
            "--check_hostname",
            True,
            "--no-verify-certificates",
        ],
    )
    assert isinstance(result.exception, DevoSenderException)
    assert "SSL conn establishment socket error" in result.exception.args[0]


def test_cli_notfound_certs(setup):
    runner = CliRunner()
    result = runner.invoke(
        data,
        [
            "--debug",
            "--address",
            setup.remote_address,
            "--port",
            "443",
            "--key",
            "not_a_folder/not_a_file",
            "--cert",
            setup.cert,
            "--chain",
            setup.ca,
            "--verify_mode",
            1,
            "--check_hostname",
            True,
        ],
    )
    assert isinstance(result.exception, SystemExit)
    assert (
        "Error: Invalid value for '--key': Path 'not_a_folder/not_a_file' does not exist."
        in result.stdout
    )


def test_cli_normal_send_without_certificates_checking(setup):
    runner = CliRunner()
    result = runner.invoke(
        data,
        [
            "--debug",
            "--address",
            setup.ssl_address,
            "--port",
            setup.ssl_port,
            "--key",
            setup.server_key,
            "--cert",
            setup.server_cert,
            "--chain",
            setup.chain,
            "--tag",
            setup.my_app,
            "--verify_mode",
            0,
            "--check_hostname",
            False,
            "--line",
            "Test line",
            "--no-verify-certificates",
        ],
    )

    assert result.exception is None
    assert int(result.output.split("Sended: ")[-1]) > 0


def test_cli_normal_send_with_certificates_checking(setup):
    runner = CliRunner()
    result = runner.invoke(
        data,
        [
            "--debug",
            "--address",
            setup.remote_address,
            "--port",
            setup.remote_port,
            "--key",
            setup.key,
            "--cert",
            setup.cert,
            "--chain",
            setup.ca,
            "--tag",
            setup.my_app,
            "--verify_mode",
            0,
            "--check_hostname",
            False,
            "--line",
            "Test line",
        ],
    )

    assert result.exception is None
    assert int(result.output.split("Sended: ")[-1]) > 0


def test_cli_normal_send_multiline_with_certificates_checking(setup):
    runner = CliRunner()
    result = runner.invoke(
        data,
        [
            "--debug",
            "--address",
            setup.remote_address,
            "--port",
            setup.remote_port,
            "--key",
            setup.key,
            "--cert",
            setup.cert,
            "--chain",
            setup.ca,
            "--tag",
            setup.my_app,
            "--verify_mode",
            0,
            "--check_hostname",
            False,
            "--multiline",
            "--file",
            setup.test_file,
        ],
    )

    assert result.exception is None
    assert int(result.output.split("Sended: ")[-1]) > 0


def test_cli_with_config_file(setup):
    if setup.config_path:
        runner = CliRunner()
        result = runner.invoke(
            data,
            ["--debug", "--config", setup.config_path, "--no-verify-certificates"],
        )

        assert result.exception is None
        assert int(result.output.split("Sended: ")[-1]) > 0


def test_cli_with_bad_json_config_file(setup):
    if setup.config_path:
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--config",
                setup.bad_json_config_path,
                "--no-verify-certificates",
            ],
        )

        assert result.exception is not None
        assert isinstance(result.exception, ConfigurationException)
        assert "Configuration file seems not to be a valid JSON file" == result.exception.args[0]


def test_cli_with_bad_yaml_config_file(setup):
    if setup.config_path:
        runner = CliRunner()
        result = runner.invoke(
            data,
            [
                "--debug",
                "--config",
                setup.bad_yaml_config_path,
                "--no-verify-certificates",
            ],
        )

        assert result.exception is not None
        assert isinstance(result.exception, ConfigurationException)
        assert "Configuration file seems not to be a valid YAML file" == result.exception.args[0]


def test_cli_escape_quotes(setup):
    runner = CliRunner()
    result = runner.invoke(
        lookup,
        [
            "--debug",
            "--address",
            setup.ssl_address,
            "--port",
            setup.ssl_port,
            "--key",
            setup.server_key,
            "--cert",
            setup.server_cert,
            "--chain",
            setup.chain,
            "--verify_mode",
            0,
            "--check_hostname",
            False,
            "-n",
            setup.lookup_name,
            "-ac",
            "FULL",
            "-f",
            setup.lookup_file,
            "-lk",
            "KEY",
            "-eq",
            "--no-verify-certificates",
        ],
    )

    assert result.exception is None
    assert result.exit_code == 0


def test_cli_not_escape_quotes(setup):
    runner = CliRunner()
    result = runner.invoke(
        lookup,
        [
            "--debug",
            "--address",
            setup.ssl_address,
            "--port",
            setup.ssl_port,
            "--key",
            setup.server_key,
            "--cert",
            setup.server_cert,
            "--chain",
            setup.chain,
            "--verify_mode",
            0,
            "--check_hostname",
            False,
            "-n",
            setup.lookup_name,
            "-ac",
            "FULL",
            "-f",
            setup.lookup_file,
            "-lk",
            "KEY",
            "--no-verify-certificates",
        ],
    )

    assert result.exception is not None
    assert result.exit_code == 64


if __name__ == "__main__":
    pytest.main()
