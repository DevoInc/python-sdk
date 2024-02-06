import pytest

import devo.api.processors as processors


@pytest.fixture(scope="module")
def setup():

    class Fixture:
        pass

    setup = Fixture()
    setup.stream_spaces = "       "
    setup.valid_json = '{"a":1, "b":2, "c":3, "d":4}'
    setup.compact_simple = '{"d":[1506439800000, "self", "email@devo.com", null, 1]}'
    setup.names = ["eventdate", "domain", "userEmail", "country", "count"]
    setup.simple_names = {
        "m": {
            "eventdate": {"type": "timestamp", "index": 0},
            "domain": {"type": "str", "index": 1},
            "userEmail": {"type": "str", "index": 2},
            "country": {"type": "str", "index": 3},
            "count": {"type": "int8", "index": 4},
        }
    }
    setup.compact_response = '{ "msg": "", "status": 0, "object": { "m": \
        { "eventdate": { "type": "timestamp", "index": 0 }, "domain": \
        { "type": "str", "index": 1 }, "userEmail": { "type": "str", \
        "index": 2 }, "country": { "type": "str", "index": 3 }, "count": \
        { "type": "int8", "index": 4 } }, "d": [ [ 1506442210000, "self", \
        "luis.xxxxx@devo.com", null, 2 ], [ 1506442220000, "self", \
        "goaquinxxx@gmail.com", null, 2 ] ] }}'

    yield setup


def test_proc_default(setup):
    assert processors.proc_default()(setup.stream_spaces) == ""


def test_proc_json(setup):
    assert processors.proc_json()(None) is None
    assert processors.proc_json()(setup.stream_spaces) is None
    assert processors.proc_json()(setup.valid_json)["b"] == 2


def test_proc_json_simple(setup):
    assert processors.proc_json_simple()(None) is None
    assert processors.proc_json_simple()(setup.stream_spaces) is None
    assert processors.proc_json_simple()(setup.valid_json)["b"] == 2


def test_proc_json_compact_to_array(setup):
    assert processors.proc_json_compact_to_array()(None) is None
    assert processors.proc_json_compact_to_array()(setup.stream_spaces) is None
    assert processors.proc_json_compact_to_array()(setup.compact_response) == [
        [1506442210000, "self", "luis.xxxxx@devo.com", None, 2],
        [1506442220000, "self", "goaquinxxx@gmail.com", None, 2],
    ]


def test_json_compact_simple_names(setup):
    assert processors.json_compact_simple_names(setup.stream_spaces) == []
    assert processors.json_compact_simple_names(setup.simple_names["m"]) == [
        "eventdate",
        "domain",
        "userEmail",
        "country",
        "count",
    ]


def test_proc_json_compact_simple_to_jobj(setup):
    assert processors.proc_json_compact_simple_to_jobj(setup.names)(setup.stream_spaces) == {}
    assert processors.proc_json_compact_simple_to_jobj(setup.names)(setup.compact_simple) == {
        "eventdate": 1506439800000,
        "domain": "self",
        "userEmail": "email@devo.com",
        "country": None,
        "count": 1,
    }


def test_proc_json_compact_simple_to_array(setup):
    assert processors.proc_json_compact_simple_to_array()(setup.stream_spaces) == []
    assert processors.proc_json_compact_simple_to_array()(setup.compact_simple) == [
        1506439800000,
        "self",
        "email@devo.com",
        None,
        1,
    ]


if __name__ == "__main__":
    pytest.main()
