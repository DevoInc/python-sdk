import json
import os
from unittest import mock
from unittest.mock import MagicMock

import pytest
from devo.api import Client
from devo.api.client import (DEFAULT_KEEPALIVE_TOKEN,
                             EMPTY_EVENT_KEEPALIVE_TOKEN, NO_KEEPALIVE_TOKEN,
                             ClientConfig)
from requests.models import Response


@pytest.fixture(scope="module")
def setup_config_path():
    """Return the path of the configuration file in resources folder"""
    module_configuration = "".join(
        [os.path.dirname(os.path.abspath(__file__)), os.sep, "resources"]
    )
    yield module_configuration


def _query_stream(response_type, result, keepAliveToken=DEFAULT_KEEPALIVE_TOKEN):
    """
    This function is used to mock the stream response from the server.
    """
    client = Client(
        retries=0,
        config={
            "address": "URI",
            "stream": True,
            "response": response_type,
            "keepAliveToken": keepAliveToken,
        },
    )
    client._make_request = MagicMock(return_value=(None, result, None))
    return client.query()


def _query_no_stream(response_type, result, keepAliveToken=DEFAULT_KEEPALIVE_TOKEN):
    """
    This function is used to mock the non-stream response from the server.
    """
    client = Client(
        retries=0,
        config={
            "address": "URI",
            "stream": False,
            "response": response_type,
            "keepAliveToken": keepAliveToken,
        },
    )
    with mock.patch("devo.api.Client._make_request") as patched_make_request:
        response = Response()
        response.status_code = 200

        if isinstance(result, str):
            response._content = result.encode("utf-8")
            response.text
            patched_make_request.return_value = (response, None, None)
        else:
            response._content = result
            patched_make_request.return_value = (response, None, None)
        return client.query()


def test_json_token_notstream():
    result = (
        '{"msg":"","timestamp":1659539571639,"cid":"a6fe6a6ec8bc",'
        '"status":0,"object":[{"eventdate":1659539580000,"count":'
        '50}  ,{"eventdate":1659539640000,"count":105}]} '
    )
    response = "json"

    response = _query_no_stream(response, result)

    assert response is not None
    data = json.loads(response)
    assert 50 == data["object"][0]["count"]
    assert 105 == data["object"][1]["count"]


def test_json_compact_token_notstream():
    result = (
        '{"msg":"","status":0,"timestamp":1659604839206,'
        '"cid":"ffe04b2e649c","object":{"m":{"eventdate":{"type":'
        '"timestamp","index":0},"count":{"type":"int8","index":1}}'
        ',"metadata":[{"name":"eventdate","type":"timestamp"},'
        '{"name":"count","type":"int8"}],"d":[       ['
        "1659604860000,18]    ,[1659604920000,58]]}} "
    )
    response = "json/compact"

    response = _query_no_stream(response, result)

    assert response is not None
    data = json.loads(response)
    assert 18 == data["object"]["d"][0][1]
    assert 58 == data["object"]["d"][1][1]


def test_json_simple_token_notstream():
    result = (
        '      {"eventdate":1659605100000,"count":16}\r\n     {'
        '"eventdate":1659605160000,"count":44}\r\n'
    )
    response = "json/simple"

    response = _query_no_stream(response, result)

    assert response is not None
    assert [16, 44] == [json.loads(event)["count"] for event in response.split("\r\n")]


def test_json_simple_token_stream():
    result = iter(
        [
            b"    ",
            b'       {"eventdate":1659615360000,"count":118}',
            b"     ",
            b' {"eventdate":1659615420000,"count":14}',
        ]
    )
    response = "json/simple"

    response = _query_stream(response, result)

    assert response is not None
    assert [118, 14] == [json.loads(event)["count"] if event.strip() else "" for event in response]


def test_json_simple_compact_token_notstream():
    result = (
        '{"m":{"eventdate":{"type":"timestamp","index":0},"count":'
        '{"type":"int8","index":1}},"metadata":[{"name":'
        '"eventdate","type":"timestamp"},{"name":"count","type":'
        '"int8"}]}\r\n       {"d":[1659605340000,10]}\r\n     {'
        '"d":[1659605400000,40]} '
    )
    response = "json/simple/compact"

    response = _query_no_stream(response, result)

    assert response is not None
    assert [10, 40] == [
        json.loads(event)["d"][1] for event in response.split("\r\n") if "d" in json.loads(event)
    ]


def test_json_simple_compact_token_stream():
    # As captured from real query
    result = iter(
        [
            b"    ",
            b'{"m":{"eventdate":{"type":"timestamp","index":0},'
            b'"count":{"type":"int8","index":1}},'
            b'"metadata":[{"name":"eventdate","type":"timestamp"}'
            b',{"name":"count","type":"int8"}]}',
            b'       {"d":[1659615780000,4]}',
            b"    ",
            b"    ",
            b'     {"d":[1659615840000,12]}',
        ]
    )
    response = "json/simple/compact"
    response = _query_stream(response, result)

    assert response is not None
    assert [4, 12] == [
        json.loads(event)["d"][1] if event.strip() else "" for event in list(response)[1:]
    ]


def test_csv_default_token_notstream():
    result = (
        "eventdate,count\n\n\n\n\n\n\n\n\n2022-08-04 10:47:00.000,"
        "59\n2022-08-04 10:48:00.000,4\n"
    )
    response = "csv"
    keepalive_token = DEFAULT_KEEPALIVE_TOKEN

    response = _query_no_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [("2022-08-04 10:47:00.000", "59"), ("2022-08-04 10:48:00.000", "4")] == [
        (event.split(",")[0], event.split(",")[1]) for event in response.split("\n")[1:]
    ]


def test_csv_empty_event_token_notstream():
    result = (
        "eventdate,count\n,\n,\n,\n,\n,\n,\n,\n,\n,\n,\n"
        "2022-08-04 10:52:00.000,40\n,\n2022-08-04 10:53:00.000,16\n "
    )
    response = "csv"
    keepalive_token = EMPTY_EVENT_KEEPALIVE_TOKEN

    response = _query_no_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [("2022-08-04 10:52:00.000", "40"), ("2022-08-04 10:53:00.000", "16")] == [
        (event.split(",")[0], event.split(",")[1]) for event in response.split("\n")[1:]
    ]


def test_csv_custom_token_notstream():
    result = (
        "eventdate,count\nTOKENTOKENTOKENTOKENTOKENTOKENTOKEN"
        "2022-08-04 10:57:00.000,18\nTOKENTOKEN"
        "2022-08-04 10:58:00.000,12\n "
    )
    response = "csv"
    keepalive_token = "TOKEN"

    response = _query_no_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [("2022-08-04 10:57:00.000", "18"), ("2022-08-04 10:58:00.000", "12")] == [
        (event.split(",")[0], event.split(",")[1]) for event in response.split("\n")[1:]
    ]


def test_csv_default_token_stream():
    result = iter(
        [
            b"eventdate,count",
            b"",
            b"",
            b"",
            b"",
            b"",
            b"",
            b"2022-08-04 12:38:00.000,6",
            b"",
            b"",
            b"",
            b"2022-08-04 12:39:00.000,36",
        ]
    )
    response = "csv"
    keepalive_token = DEFAULT_KEEPALIVE_TOKEN

    response = _query_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 12:38:00.000", "6"),
        ("2022-08-04 12:39:00.000", "36"),
    ] == [(event.split(",")[0], event.split(",")[1]) for event in response]


def test_csv_empty_event_token_stream():
    result = iter(
        [
            b"eventdate,count",
            b",",
            b",",
            b",",
            b",",
            b",",
            b",",
            b",",
            b"2022-08-04 12:41:00.000,4",
            b",",
            b",",
            b",",
            b",",
            b"2022-08-04 12:42:00.000,14",
        ]
    )
    response = "csv"
    keepalive_token = EMPTY_EVENT_KEEPALIVE_TOKEN

    response = _query_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 12:41:00.000", "4"),
        ("2022-08-04 12:42:00.000", "14"),
    ] == [(event.split(",")[0], event.split(",")[1]) for event in response]


def test_csv_custom_token_stream():
    result = iter(
        [
            b"eventdate,count",
            b"TOKENTOKENTOKENTOKENTOKENTOKEN" b"2022-08-04 12:44:00.000,4",
            b"TOKENTOKENTOKEN2022-08-04 12:45:00.000,12",
        ]
    )
    response = "csv"
    keepalive_token = "TOKEN"

    response = _query_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 12:44:00.000", "4"),
        ("2022-08-04 12:45:00.000", "12"),
    ] == [(event.split(",")[0], event.split(",")[1]) for event in response]


def test_tsv_default_token_notstream():
    result = (
        "eventdate\tcount\n\n\n\n\n\n\n2022-08-04 11:10:00.000\t4"
        "\n\n\n\n\n2022-08-04 11:11:00.000\t169\n"
    )
    response = "tsv"
    keepalive_token = DEFAULT_KEEPALIVE_TOKEN

    response = _query_no_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 11:10:00.000", "4"),
        ("2022-08-04 11:11:00.000", "169"),
    ] == [(event.split("\t")[0], event.split("\t")[1]) for event in response.split("\n")]


def test_tsv_empty_event_token_notstream():
    result = (
        "eventdate\tcount\n\t\n\t\n\t\n\t\n\t\n\t\n\t\n"
        "2022-08-04 11:06:00.000\t24\n\t\n\t\n"
        "2022-08-04 11:07:00.000\t86\n "
    )
    response = "tsv"
    keepalive_token = EMPTY_EVENT_KEEPALIVE_TOKEN

    response = _query_no_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 11:06:00.000", "24"),
        ("2022-08-04 11:07:00.000", "86"),
    ] == [(event.split("\t")[0], event.split("\t")[1]) for event in response.split("\n")]


def test_tsv_custom_token_notstream():
    result = (
        "eventdate\tcount\nTOKENTOKENTOKENTOKENTOKENTOKENTOKEN"
        "2022-08-04 11:02:00.000\t8\nTOKENTOKEN"
        "2022-08-04 11:03:00.000\t22\n "
    )
    response = "tsv"
    keepalive_token = "TOKEN"

    response = _query_no_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 11:02:00.000", "8"),
        ("2022-08-04 11:03:00.000", "22"),
    ] == [(event.split("\t")[0], event.split("\t")[1]) for event in response.split("\n")]


def test_tsv_default_token_stream():
    result = iter(
        [
            b"eventdate\tcount",
            b"",
            b"",
            b"",
            b"",
            b"",
            b"",
            b"2022-08-04 12:48:00.000\t4",
            b"",
            b"",
            b"",
            b"2022-08-04 12:49:00.000\t12",
        ]
    )
    response = "tsv"
    keepalive_token = DEFAULT_KEEPALIVE_TOKEN

    response = _query_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 12:48:00.000", "4"),
        ("2022-08-04 12:49:00.000", "12"),
    ] == [(event.split("\t")[0], event.split("\t")[1]) for event in response]


def test_tsv_empty_event_token_stream():
    result = iter(
        [
            b"eventdate\tcount",
            b"\t",
            b"\t",
            b"\t",
            b"\t",
            b"\t",
            b"\t",
            b"\t",
            b"\t",
            b"\t",
            b"2022-08-04 12:51:00.000\t12",
            b"\t",
            b"\t",
            b"2022-08-04 12:52:00.000\t4",
        ]
    )
    response = "tsv"
    keepalive_token = EMPTY_EVENT_KEEPALIVE_TOKEN

    response = _query_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 12:51:00.000", "12"),
        ("2022-08-04 12:52:00.000", "4"),
    ] == [(event.split("\t")[0], event.split("\t")[1]) for event in response]


def test_tsv_custom_token_stream():
    result = iter(
        [
            b"eventdate\tcount",
            b"TOKENTOKENTOKENTOKENTOKENTOKENTOKEN" b"2022-08-04 12:54:00.000\t8",
            b"TOKENTOKEN2022-08-04 12:55:00.000\t10",
        ]
    )
    response = "tsv"
    keepalive_token = "TOKEN"

    response = _query_stream(response, result, keepAliveToken=keepalive_token)

    assert response is not None
    assert [
        ("eventdate", "count"),
        ("2022-08-04 12:54:00.000", "8"),
        ("2022-08-04 12:55:00.000", "10"),
    ] == [(event.split("\t")[0], event.split("\t")[1]) for event in response]


def test_msgpack_notstream(setup_config_path):
    mgspack_file = setup_config_path + os.sep + "msgpack_no_keepalive"
    with open(mgspack_file, "rb") as f:
        result = f.read()
    keepalive_token = NO_KEEPALIVE_TOKEN

    response = _query_no_stream("msgpack", result, keepAliveToken=keepalive_token)

    assert response is not None
    assert response == result


def test_xls_notstream(setup_config_path):
    xls_file = setup_config_path + os.sep + "xls_default.xls"
    with open(xls_file, "rb") as f:
        result = f.read()
    keepalive_token = DEFAULT_KEEPALIVE_TOKEN

    response = _query_no_stream("xls", result, keepAliveToken=keepalive_token)

    assert response is not None
    assert response == result


def test_keepAliveToken_csv():
    config = ClientConfig(response="csv")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is not None
    assert config.keepAliveToken == DEFAULT_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is not None
    assert config.keepAliveToken == DEFAULT_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is not None
    assert config.keepAliveToken == "TEST"


def test_keepAliveToken_tsv():
    config = ClientConfig(response="tsv")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is not None
    assert config.keepAliveToken == DEFAULT_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is not None
    assert config.keepAliveToken == DEFAULT_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is not None
    assert config.keepAliveToken == "TEST"


def test_keepAliveToken_xls():
    config = ClientConfig(response="xls")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN


def test_keepAliveToken_msgpack():
    config = ClientConfig(response="msgpack")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN


def test_keepAliveToken_json():
    config = ClientConfig(response="json")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN


def test_keepAliveToken_json_compact():
    config = ClientConfig(response="json/compact")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN


def test_keepAliveToken_json_simple():
    config = ClientConfig(response="json/simple")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN


def test_keepAliveToken_json_simple_compact():
    config = ClientConfig(response="json/simple/compact")

    config.set_keepalive_token(keepAliveToken=DEFAULT_KEEPALIVE_TOKEN)
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token()
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN

    config.set_keepalive_token(keepAliveToken="TEST")
    assert config.keepAliveToken is None
    assert config.keepAliveToken == NO_KEEPALIVE_TOKEN


if __name__ == "__main__":
    pytest.main()
