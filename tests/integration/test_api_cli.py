import json
import os
import tempfile
from datetime import datetime, timedelta
from ssl import CERT_NONE

import pytest
from click.testing import CliRunner
from helpers.ip_validation import is_valid_ip

from devo.api.client import ERROR_MSGS, DevoClientException
from devo.api.scripts.client_cli import query
from devo.common import Configuration
from devo.common.loadenv.load_env import load_env_file
from devo.sender.data import Sender, SenderConfigSSL

# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


class Fixture:
    """Empty fixture class used for testing."""

    pass


@pytest.fixture(scope="session", autouse=True)
def sending_config():
    """Fixture for sending configuration."""

    setup = Fixture()

    setup.res_path = os.path.dirname(os.path.abspath(__file__)) + os.sep + "resources"
    setup.remote_address = os.getenv("DEVO_REMOTE_SENDER_SERVER", "collector-us.devo.io")
    setup.remote_port = int(os.getenv("DEVO_REMOTE_SENDER_PORT", 443))
    setup.remote_server_key = os.getenv(
        "DEVO_SENDER_KEY", f"{setup.res_path}/certs/us/devo_services.key"
    )
    setup.remote_server_cert = os.getenv(
        "DEVO_SENDER_CERT", f"{setup.res_path}/certs/us/devo_services.crt"
    )
    setup.remote_server_chain = os.getenv(
        "DEVO_SENDER_CHAIN", f"{setup.res_path}/certs/us/chain.crt"
    )

    setup.hostname = "python-sdk-test-hostname"
    # setup.test_tag_with_ip = "demo.ecommerce.data"
    # setup.test_msg_with_ip = (
    #     "127.0.0.1 [01/Apr/2024:13:04:36 +0000]"
    #     "GET /product.screen?product_id=943-55PAU-0X9CV&JSESSIONID=SD10SL1FF5ADFF8 HTTP 1.1 200 2109 "
    #     '"http://www.google.com/category.screen?category_id=SHIRTS&JSESSIONID=SD10SL1FF5ADFF8" '
    #     '"Opera/9.20 (Windows NT 6.0; U; en)" "3djv1l0ebi7cmsai1131pf2a65:-" 753'
    # )
    setup.test_tag_with_ip = os.getenv("DEVO_API_QUERY_TAG_WITH_IP", "test.keep.types")
    setup.test_msg_with_ip = os.getenv("DEVO_API_QUERY_MSG_WITH_IP", "ip4=127.0.0.1")

    yield setup


def send_test_log(sending_config: Fixture):
    """Fixture for sending data."""

    # Send a log to demo.ecommerce.data to have data to query with an IPV4 address
    try:
        engine_config = SenderConfigSSL(
            address=(sending_config.remote_address, sending_config.remote_port),
            key=sending_config.remote_server_key,
            cert=sending_config.remote_server_cert,
            chain=sending_config.remote_server_chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender(engine_config)
        con.send(
            tag=sending_config.test_tag_with_ip,
            msg=sending_config.test_msg_with_ip,
            hostname=sending_config.hostname,
        )
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        day_of_month = yesterday.day
        yesterday_tag = f"(usd.family[{day_of_month}]){sending_config.test_tag_with_ip}"
        raw_log = (
            f'<14>{yesterday.strftime("%b %d %H:%M:%S")} '
            f"{sending_config.hostname} "
            f"{yesterday_tag}: "
            f"{sending_config.test_msg_with_ip}"
        )
        con.send_raw(raw_log)
        con.close()
    except Exception as error:
        pytest.fail("Problems with test: %s" % str(error))


@pytest.fixture(scope="session", autouse=True)
def api_config(sending_config):
    """Fixture for API configuration."""

    send_test_log(sending_config)

    setup = Fixture()

    setup.query = os.getenv("DEVO_API_QUERY", "from test.keep.types select ip4 limit 1")
    setup.query_no_results = (
        'from siem.logtrust.web.activity where method = "OTHER" select method limit 1'
    )

    setup.query_with_ip = os.getenv(
        "DEVO_API_QUERY_WITH_IP", "from test.keep.types select ip4 limit 1"
    )
    setup.field_with_ip = os.getenv("DEVO_API_FIELD_WITH_IP", "ip4")
    setup.api_address = os.getenv("DEVO_API_ADDRESS", "https://apiv2-us.devo.com/search/query")
    setup.api_key = os.getenv("DEVO_API_KEY", None)
    setup.api_secret = os.getenv("DEVO_API_SECRET", None)
    setup.api_token = os.getenv("DEVO_API_TOKEN", None)
    setup.query_id = os.getenv("DEVO_API_QUERYID", None)
    setup.user = os.getenv("DEVO_API_USER", "python-sdk-user")
    setup.comment = os.getenv("DEVO_API_COMMENT", None)
    setup.app_name = "testing-app_name"

    configuration = Configuration()
    configuration.set(
        "api",
        {
            "query": setup.query,
            "address": setup.api_address,
            "key": setup.api_key,
            "secret": setup.api_secret,
            "token": setup.api_token,
            "query_id": setup.query_id,
            "user": setup.user,
            "comment": setup.comment,
            "app_name": setup.app_name,
        },
    )

    setup.config_path = os.path.join(tempfile.gettempdir(), "devo_api_tests_config.json")
    configuration.save(path=setup.config_path)

    yield setup

    if os.path.exists(setup.config_path):
        os.remove(setup.config_path)


def test_query_args():
    runner = CliRunner()
    result = runner.invoke(query, [])
    assert "Usage: query [OPTIONS]" in result.stdout


def test_not_credentials(api_config):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            api_config.query,
            "--address",
            api_config.api_address,
        ],
    )

    assert isinstance(result.exception, DevoClientException)
    assert ERROR_MSGS["no_auth"] in result.exception.args[0]


def test_bad_url(api_config):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            api_config.query,
            "--address",
            "error-apiv2-us.logtrust.com/search/query",
            "--key",
            api_config.api_key,
            "--secret",
            api_config.api_secret,
        ],
    )
    assert isinstance(result.exception, DevoClientException)
    assert "Failed to establish a new connection" in result.exception.args[0]


def test_bad_credentials(api_config):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            api_config.query,
            "--address",
            api_config.api_address,
            "--key",
            "aaa",
            "--secret",
            api_config.api_secret,
        ],
    )
    assert isinstance(result.exception, DevoClientException)
    assert result.exception.code == 12


def test_normal_query(api_config):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            api_config.query,
            "--address",
            api_config.api_address,
            "--key",
            api_config.api_key,
            "--secret",
            api_config.api_secret,
        ],
    )

    assert result.exception is None
    assert result.exit_code == 0
    assert '{"m":{"eventdate":{"type":"timestamp","index":0' in result.output


def test_with_config_file(api_config):
    if api_config.config_path:
        runner = CliRunner()

        result = runner.invoke(
            query,
            [
                "--debug",
                "--from",
                "1d",
                "--query",
                api_config.query,
                "--config",
                api_config.config_path,
            ],
        )
        assert result.exception is None
        assert result.exit_code == 0
        assert '{"m":{"eventdate":{"type":"timestamp","index":0' in result.output


def test_query_with_ip_as_int(api_config):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            api_config.query_with_ip,
            "--address",
            api_config.api_address,
            "--key",
            api_config.api_key,
            "--secret",
            api_config.api_secret,
        ],
    )

    assert result.exception is None
    assert result.exit_code == 0
    resp_list = result.output.split("\n")
    resp_metadata = json.loads(resp_list[0])
    resp_data = json.loads(resp_list[1])
    assert api_config.field_with_ip in resp_metadata["m"]
    assert "ip4" in resp_metadata["m"][api_config.field_with_ip]["type"]
    assert isinstance(resp_data["d"][0], int)


def test_query_with_ip_as_str(api_config):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            api_config.query_with_ip,
            "--address",
            api_config.api_address,
            "--key",
            api_config.api_key,
            "--secret",
            api_config.api_secret,
            "--ip-as-string",
        ],
    )

    assert result.exception is None
    assert result.exit_code == 0
    resp_list = result.output.split("\n")
    resp_metadata = json.loads(resp_list[0])
    resp_data = json.loads(resp_list[1])
    assert api_config.field_with_ip in resp_metadata["m"]
    assert "ip4" in resp_metadata["m"][api_config.field_with_ip]["type"]
    ip = resp_data["d"][0]
    assert isinstance(ip, str)
    assert is_valid_ip(ip)


if __name__ == "__main__":
    pytest.main()
