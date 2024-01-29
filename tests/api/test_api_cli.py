import os
import tempfile

import pytest
from click.testing import CliRunner
from devo.api.client import ERROR_MSGS, DevoClientException
from devo.api.scripts.client_cli import query
from devo.common import Configuration
from devo.common.loadenv.load_env import load_env_file

# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


@pytest.fixture(scope="module", autouse=True)
def setup():
    class Fixture:
        pass

    setup = Fixture()
    setup.query = os.getenv(
        "DEVO_API_QUERY", "from siem.logtrust.web.activity select eventdate limit 1"
    )
    setup.app_name = "testing-app_name"
    setup.uri = os.getenv("DEVO_API_ADDRESS", "https://apiv2-us.devo.com/search/query")
    setup.key = os.getenv("DEVO_API_KEY", None)
    setup.secret = os.getenv("DEVO_API_SECRET", None)
    setup.token = os.getenv("DEVO_AUTH_TOKEN", None)
    setup.query_id = os.getenv("DEVO_API_QUERYID", None)
    setup.user = os.getenv("DEVO_API_USER", "python-sdk-user")
    setup.comment = os.getenv("DEVO_API_COMMENT", None)

    configuration = Configuration()
    configuration.set(
        "api",
        {
            "query": setup.query,
            "address": setup.uri,
            "key": setup.key,
            "secret": setup.secret,
            "token": setup.token,
            "query_id": setup.query_id,
            "user": setup.user,
            "comment": setup.comment,
            "app_name": setup.app_name,
        },
    )

    setup.config_path = os.path.join(tempfile.gettempdir(), "devo_api_tests_config.json")
    configuration.save(path=setup.config_path)

    yield setup  # Run test code

    if os.path.exists(setup.config_path):
        os.remove(setup.config_path)


def test_query_args():
    runner = CliRunner()
    result = runner.invoke(query, [])
    assert "Usage: query [OPTIONS]" in result.stdout


def test_not_credentials(setup):
    runner = CliRunner()
    result = runner.invoke(
        query,
        ["--debug", "--from", "1d", "--query", setup.query, "--address", setup.uri],
    )

    assert isinstance(result.exception, DevoClientException)
    assert ERROR_MSGS["no_auth"] in result.exception.args[0]


def test_bad_url(setup):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            setup.query,
            "--address",
            "error-apiv2-us.logtrust.com/search/query",
            "--key",
            setup.key,
            "--secret",
            setup.secret,
        ],
    )
    assert isinstance(result.exception, DevoClientException)
    assert "Failed to establish a new connection" in result.exception.args[0]


def test_bad_credentials(setup):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            setup.query,
            "--address",
            setup.uri,
            "--key",
            "aaa",
            "--secret",
            setup.secret,
        ],
    )
    assert isinstance(result.exception, DevoClientException)
    assert result.exception.code == 12


def test_normal_query(setup):
    runner = CliRunner()
    result = runner.invoke(
        query,
        [
            "--debug",
            "--from",
            "1d",
            "--query",
            setup.query,
            "--address",
            setup.uri,
            "--key",
            setup.key,
            "--secret",
            setup.secret,
        ],
    )

    assert result.exception is None
    assert result.exit_code == 0
    assert '{"m":{"eventdate":{"type":"timestamp","index":0' in result.output


def test_with_config_file(setup):
    if setup.config_path:
        runner = CliRunner()

        result = runner.invoke(
            query,
            [
                "--debug",
                "--from",
                "1d",
                "--query",
                setup.query,
                "--config",
                setup.config_path,
            ],
        )
        assert result.exception is None
        assert result.exit_code == 0
        assert '{"m":{"eventdate":{"type":"timestamp","index":0' in result.output


if __name__ == "__main__":
    pytest.main()
