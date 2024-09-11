import json
import os
import tempfile
import types
from datetime import datetime, timedelta
import zoneinfo
UTC = zoneinfo.ZoneInfo("UTC")

from ssl import CERT_NONE

import pytest
import stopit
from ip_validation import is_valid_ip

from devo.api import Client, ClientConfig, DevoClientException
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

    setup = sending_config
    send_test_log(setup)

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


def test_from_dict(api_config):
    api = Client(
        config={
            "key": api_config.api_key,
            "secret": api_config.api_secret,
            "address": api_config.api_address,
            "user": api_config.user,
            "app_name": api_config.app_name,
        }
    )

    assert isinstance(api, Client)


def test_simple_query(api_config):
    config = ClientConfig(stream=False, response="json")

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=config,
        retries=3,
    )

    result = api.query(query=api_config.query)
    assert result is not None
    assert len(json.loads(result)["object"]) > 0


def test_token(api_config):
    api = Client(
        auth={"token": api_config.api_token},
        address=api_config.api_address,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(query=api_config.query)
    assert result is not None
    assert len(json.loads(result)["object"]) > 0


def test_query_id(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(stream=False, response="json"),
        retries=5,
    )
    result = api.query(query_id=api_config.query_id)
    assert result is not None
    assert result != {}
    assert isinstance(len(json.loads(result)["object"]), int)


def test_query_yesterday_to_today(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(
        query=api_config.query_with_ip, dates={"from": "yesterday()", "to": "today()"}
    )
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_query_from_seven_days(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(query=api_config.query, dates={"from": "now()-7*day()", "to": "now()"})
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_query_from_fixed_dates(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(
        query=api_config.query,
        dates={
            "from": datetime.now(UTC).strftime("%Y-%m-%d"),
            "to": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        },
    )
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_stream_query(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="json/simple"),
        retries=3,
    )
    result = api.query(query=api_config.query)
    assert isinstance(result, types.GeneratorType)
    result = list(result)
    assert len(result) == 1


def test_stream_query_no_results_bounded_dates(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="json/simple"),
        retries=3,
    )
    result = api.query(query=api_config.query_no_results, dates={"from": "1h", "to": "now()"})
    assert isinstance(result, types.GeneratorType)
    result = list(result)
    assert len(result) == 0


def test_stream_query_no_results_unbounded_dates(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="json/simple"),
        retries=3,
    )
    result = api.query(query=api_config.query_no_results)
    assert isinstance(result, types.GeneratorType)

    try:
        with stopit.ThreadingTimeout(3) as to_ctx_mgr:
            result = list(result)
    except DevoClientException:
        # This exception is sent because
        # devo.api.client.Client._make_request catches the
        # stopit.TimeoutException, but the latter is not
        # wrapped, so we cannot obtain it from here.
        assert to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT


def test_pragmas(api_config):
    """Test the api when the pragma comment.free is used"""
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="json", stream=False),
        retries=3,
    )
    api.config.set_user(user=api_config.user)
    api.config.set_app_name(app_name=api_config.app_name)
    result = api.query(query=api_config.query, comment=api_config.comment)
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_pragmas_not_comment_free(api_config):
    """Test the api when the pragma comment.free is not used"""
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="json", stream=False),
        retries=3,
    )
    api.config.set_user(user=api_config.user)
    api.config.set_app_name(app_name=api_config.app_name)
    result = api.query(query=api_config.query)
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


@pytest.mark.skip(reason="This is an internal functionality, not intended for external use")
def test_unsecure_http_query(api_config):
    """
    This test is intended for checking unsecure HTTP requests. Devo will
    NEVER provide an unsecure HTTP endpoint for API REST services.
    Therefore, you are not going to need to use or test this functionality.
    In order to enable UNSECURE_HTTP environment var should be TRUE.
    The endpoint is served by https://httpbin.org/. You can run with
    `docker run -p 80:80 kennethreitz/httpbin`. It will expose an HTTP
    service at port 80.
    The URL `http://localhost:80/anything` will answer with the content of
    the request.
    """
    os.environ["UNSECURE_HTTP"] = "TRUE"
    config = ClientConfig(stream=False, response="json")

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address="localhost:80/anything",
        config=config,
        retries=3,
    )

    result = api.query(query=api_config.query)
    assert result is not None
    assert "json" in json.loads(result)
    assert "query" in json.loads(result)["json"]


def test_stream_mode_not_supported_xls(api_config):
    """Test the api stream mode is not supported for xls format"""

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="xls"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_stream_mode_not_supported_json(api_config):
    """Test the api stream mode is not supported for json format"""

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="json"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_stream_mode_not_supported_json_compact(api_config):
    """Test the api stream mode is not supported for json/compact format"""

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="json/compact"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_stream_mode_not_supported_msgpack(api_config):
    """Test the api stream mode is not supported for msgpack format"""

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(response="msgpack"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_xls_future_queries(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(stream=False, response="xls"),
    )

    with pytest.raises(Exception) as context:
        _ = api.query(query=api_config.query, dates={"from": "now()", "to": "now()+60*second()"})

    assert isinstance(context.value, DevoClientException)
    assert (
        context.value.args[0] == "Modes 'xls' and 'msgpack' does not support future "
        "queries because KeepAlive tokens are not available "
        "for those resonses type"
    )


def test_msgpack_future_queries(api_config):
    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=ClientConfig(stream=False, response="msgpack"),
    )

    with pytest.raises(Exception) as context:
        _ = api.query(query=api_config.query, dates={"from": "now()", "to": "now()+60*second()"})

    assert isinstance(context.value, DevoClientException)
    assert (
        context.value.args[0] == "Modes 'xls' and 'msgpack' does not support future "
        "queries because KeepAlive tokens are not available "
        "for those resonses type"
    )


def test_query_with_ip_as_int(api_config):
    config = ClientConfig(stream=False, response="json")

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=config,
        retries=3,
    )

    result = api.query(query=api_config.query_with_ip)
    assert result is not None
    res_obj = json.loads(result)["object"]
    assert len(res_obj) > 0
    resp_data = res_obj[0]
    assert isinstance(resp_data[api_config.field_with_ip], int)


def test_query_with_ip_as_string(api_config):
    config = ClientConfig(stream=False, response="json")

    api = Client(
        auth={"key": api_config.api_key, "secret": api_config.api_secret},
        address=api_config.api_address,
        config=config,
        retries=3,
    )

    result = api.query(query=api_config.query_with_ip, ip_as_string=True)
    assert result is not None
    res_obj = json.loads(result)["object"]
    assert len(res_obj) > 0
    resp_data = res_obj[0]
    ip = resp_data[api_config.field_with_ip]
    assert isinstance(ip, str)
    assert is_valid_ip(ip)


if __name__ == "__main__":
    pytest.main()
