import json
import os
import types
from time import gmtime, strftime

import pytest
import stopit
from devo.api import Client, ClientConfig, DevoClientException
from devo.common.loadenv.load_env import load_env_file

# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


@pytest.fixture(scope="module", autouse=True)
def setup():

    class Fixture:
        pass

    setup = Fixture()
    setup.query = os.getenv(
        "DEVO_API_QUERY", "from siem.logtrust.web.activity select method limit 1"
    )
    setup.query_no_results = (
        'from siem.logtrust.web.activity where method = "OTHER" select method limit 1'
    )
    setup.app_name = "testing-app_name"
    setup.uri = os.getenv("DEVO_API_ADDRESS", "https://apiv2-us.devo.com/search/query")
    setup.key = os.getenv("DEVO_API_KEY", None)
    setup.secret = os.getenv("DEVO_API_SECRET", None)
    setup.token = os.getenv("DEVO_API_TOKEN", None)
    setup.query_id = os.getenv("DEVO_API_QUERYID", None)
    setup.user = os.getenv("DEVO_API_USER", "python-sdk-user")
    setup.comment = os.getenv("DEVO_API_COMMENT", None)

    yield setup  # Run test code


def test_from_dict(setup):
    api = Client(
        config={
            "key": setup.key,
            "secret": setup.secret,
            "address": setup.uri,
            "user": setup.user,
            "app_name": setup.app_name,
        }
    )

    assert isinstance(api, Client)


def test_simple_query(setup):
    config = ClientConfig(stream=False, response="json")

    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=config,
        retries=3,
    )

    result = api.query(query=setup.query)
    assert result is not None
    assert len(json.loads(result)["object"]) > 0


def test_token(setup):
    api = Client(
        auth={"token": setup.token},
        address=setup.uri,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(query=setup.query)
    assert result is not None
    assert len(json.loads(result)["object"]) > 0


def test_query_id(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(stream=False, response="json"),
        retries=5,
    )
    result = api.query(query_id=setup.query_id)
    assert result is not None
    assert result != {}
    assert isinstance(len(json.loads(result)["object"]), int)


def test_query_yesterday_to_today(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(query=setup.query, dates={"from": "yesterday()", "to": "today()"})
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_query_from_seven_days(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(query=setup.query, dates={"from": "now()-7*day()", "to": "now()"})
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_query_from_fixed_dates(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(stream=False, response="json"),
        retries=3,
    )
    result = api.query(
        query=setup.query,
        dates={
            "from": strftime("%Y-%m-%d", gmtime()),
            "to": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
        },
    )
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_stream_query(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="json/simple"),
        retries=3,
    )
    result = api.query(query=setup.query)
    assert isinstance(result, types.GeneratorType)
    result = list(result)
    assert len(result) == 1


def test_stream_query_no_results_bounded_dates(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="json/simple"),
        retries=3,
    )
    result = api.query(query=setup.query_no_results, dates={"from": "1h", "to": "now()"})
    assert isinstance(result, types.GeneratorType)
    result = list(result)
    assert len(result) == 0


def test_stream_query_no_results_unbounded_dates(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="json/simple"),
        retries=3,
    )
    result = api.query(query=setup.query_no_results)
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


def test_pragmas(setup):
    """Test the api when the pragma comment.free is used"""
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="json", stream=False),
        retries=3,
    )
    api.config.set_user(user=setup.user)
    api.config.set_app_name(app_name=setup.app_name)
    result = api.query(query=setup.query, comment=setup.comment)
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


def test_pragmas_not_comment_free(setup):
    """Test the api when the pragma comment.free is not used"""
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="json", stream=False),
        retries=3,
    )
    api.config.set_user(user=setup.user)
    api.config.set_app_name(app_name=setup.app_name)
    result = api.query(query=setup.query)
    assert result is not None
    assert len(json.loads(result)["object"]) == 1


@pytest.mark.skip(reason="This is an internal functionality, not intended for external use")
def test_unsecure_http_query(setup):
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
        auth={"key": setup.key, "secret": setup.secret},
        address="localhost:80/anything",
        config=config,
        retries=3,
    )

    result = api.query(query=setup.query)
    assert result is not None
    assert "json" in json.loads(result)
    assert "query" in json.loads(result)["json"]


def test_stream_mode_not_supported_xls(setup):
    """Test the api stream mode is not supported for xls format"""

    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="xls"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_stream_mode_not_supported_json(setup):
    """Test the api stream mode is not supported for json format"""

    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="json"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_stream_mode_not_supported_json_compact(setup):
    """Test the api stream mode is not supported for json/compact format"""

    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="json/compact"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_stream_mode_not_supported_msgpack(setup):
    """Test the api stream mode is not supported for msgpack format"""

    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(response="msgpack"),
    )

    stremaAvailable = Client.stream_available(api.config.response)
    assert stremaAvailable is not None
    assert stremaAvailable is False


def test_xls_future_queries(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(stream=False, response="xls"),
    )

    with pytest.raises(Exception) as context:
        _ = api.query(query=setup.query, dates={"from": "now()", "to": "now()+60*second()"})

    assert isinstance(context.value, DevoClientException)
    assert (
        context.value.args[0] == "Modes 'xls' and 'msgpack' does not support future "
        "queries because KeepAlive tokens are not available "
        "for those resonses type"
    )


def test_msgpack_future_queries(setup):
    api = Client(
        auth={"key": setup.key, "secret": setup.secret},
        address=setup.uri,
        config=ClientConfig(stream=False, response="msgpack"),
    )

    with pytest.raises(Exception) as context:
        _ = api.query(query=setup.query, dates={"from": "now()", "to": "now()+60*second()"})

    assert isinstance(context.value, DevoClientException)
    assert (
        context.value.args[0] == "Modes 'xls' and 'msgpack' does not support future "
        "queries because KeepAlive tokens are not available "
        "for those resonses type"
    )


if __name__ == "__main__":
    pytest.main()
