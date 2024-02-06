import os

import pytest

from devo.common import Configuration


@pytest.fixture(scope="module")
def file_configuration():
    """Return the path of the configuration file in resources folder"""
    file_configuration = "".join(
        [
            os.path.dirname(os.path.abspath(__file__)),
            os.sep,
            "resources",
            os.sep,
            "testfile_config",
        ]
    )
    yield file_configuration


def test_load_config():
    file_path = "bad_file.ini"
    config = Configuration()
    with pytest.raises(Exception) as context:
        config.load_config(file_path)

    assert f"Configuration file type unknown or not supported: {file_path}" in str(
        context.exconly()
    )


def test_load_directly(file_configuration):
    config = Configuration(file_configuration + ".yaml")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_get_keys_chain(file_configuration):
    config = Configuration(file_configuration + ".yaml")
    assert config.get(("devo", "die")) == "hard"


def test_get_keys_chain_in_array(file_configuration):
    config = Configuration(file_configuration + ".yaml")
    assert config.get(("devo", "die")) == "hard"


def test_add_key(file_configuration):
    config = Configuration(file_configuration + ".yaml")
    config.set("logtrust", "old")
    assert config["logtrust"] == "old"


def test_add_key_chain(file_configuration):
    config = Configuration(file_configuration + ".yaml")
    config.set(["devo", "old", "name"], "logtrust")
    assert config["devo"]["old"]["name"] == "logtrust"
    assert config.get(("devo", "old", "name")) == "logtrust"


def test_save(file_configuration):
    config = Configuration(file_configuration + ".yaml")
    config.save(file_configuration + ".bak")

    if os.path.isfile(file_configuration + ".bak"):
        os.remove(file_configuration + ".bak")
    else:
        raise Exception("File not found")


def test_load_json(file_configuration):
    config = Configuration()
    config.load_json(file_configuration + ".json")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_load_section_json(file_configuration):
    config = Configuration(file_configuration + ".json", "api")
    assert config == {"velazquez": "Then I am beautiful?"}


def test_load_yaml(file_configuration):
    config = Configuration()
    config.load_yaml(file_configuration + ".yaml")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_load_section_yaml(file_configuration):
    config = Configuration(file_configuration + ".yaml", "devo")
    assert config == {"die": "hard"}


def test_mix_json(file_configuration):
    config = Configuration(file_configuration + ".json")
    config.mix({"test": "ok"})
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
        "test": "ok",
    }


def test_mix_yaml(file_configuration):
    config = Configuration(file_configuration + ".yaml")
    config.mix({"test": "ok"})
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
        "test": "ok",
    }


if __name__ == "__main__":
    pytest.main()
