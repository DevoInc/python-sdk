import os

import pytest
from devo.common import Configuration


@pytest.fixture(scope="module")
def setup():
    """Return the path of the configuration file in resources folder"""
    module_configuration = "".join(
        [
            os.path.dirname(os.path.abspath(__file__)),
            os.sep,
            "resources",
            os.sep,
            "testfile_config",
        ]
    )
    yield module_configuration


def test_load_config():
    file_path = "bad_file.ini"
    config = Configuration()
    with pytest.raises(Exception) as context:
        config.load_config(file_path)

    assert f"Configuration file type unknown or not supported: {file_path}" in str(
        context.exconly()
    )


def test_load_directly(setup):
    config = Configuration(setup + ".yaml")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_get_keys_chain(setup):
    config = Configuration(setup + ".yaml")
    assert config.get(("devo", "die")) == "hard"


def test_get_keys_chain_in_array(setup):
    config = Configuration(setup + ".yaml")
    assert config.get(("devo", "die")) == "hard"


def test_add_key(setup):
    config = Configuration(setup + ".yaml")
    config.set("logtrust", "old")
    assert config["logtrust"] == "old"


def test_add_key_chain(setup):
    config = Configuration(setup + ".yaml")
    config.set(["devo", "old", "name"], "logtrust")
    assert config["devo"]["old"]["name"] == "logtrust"
    assert config.get(("devo", "old", "name")) == "logtrust"


def test_save(setup):
    config = Configuration(setup + ".yaml")
    config.save(setup + ".bak")

    if os.path.isfile(setup + ".bak"):
        os.remove(setup + ".bak")
    else:
        raise Exception("File not found")


def test_load_json(setup):
    config = Configuration()
    config.load_json(setup + ".json")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_load_section_json(setup):
    config = Configuration(setup + ".json", "api")
    assert config == {"velazquez": "Then I am beautiful?"}


def test_load_yaml(setup):
    config = Configuration()
    config.load_yaml(setup + ".yaml")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_load_section_yaml(setup):
    config = Configuration(setup + ".yaml", "devo")
    assert config == {"die": "hard"}


def test_mix_json(setup):
    config = Configuration(setup + ".json")
    config.mix({"test": "ok"})
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
        "test": "ok",
    }


def test_mix_yaml(setup):
    config = Configuration(setup + ".yaml")
    config.mix({"test": "ok"})
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
        "test": "ok",
    }


if __name__ == "__main__":
    pytest.main()
