import os

import pytest
from devo.common import Configuration


@pytest.fixture(scope="module")
def setup_config_path():
    module_configuration = "%s%stestfile_config" % (
        os.path.dirname(os.path.abspath(__file__)),
        os.sep,
    )
    return module_configuration


def test_load_config():
    file_path = "bad_file.ini"
    config = Configuration()
    with pytest.raises(Exception) as context:
        config.load_config(file_path)

    assert f"Configuration file type unknown or not supported: {file_path}" in str(
        context.exconly()
    )


def test_load_directly(setup_config_path):
    config = Configuration(setup_config_path + ".yaml")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_get_keys_chain(setup_config_path):
    config = Configuration(setup_config_path + ".yaml")
    assert config.get(("devo", "die")) == "hard"


def test_get_keys_chain_in_array(setup_config_path):
    config = Configuration(setup_config_path + ".yaml")
    assert config.get(("devo", "die")) == "hard"


def test_add_key(setup_config_path):
    config = Configuration(setup_config_path + ".yaml")
    config.set("logtrust", "old")
    assert config["logtrust"] == "old"


def test_add_key_chain(setup_config_path):
    config = Configuration(setup_config_path + ".yaml")
    config.set(["devo", "old", "name"], "logtrust")
    assert config["devo"]["old"]["name"] == "logtrust"
    assert config.get(("devo", "old", "name")) == "logtrust"


def test_save(setup_config_path):
    config = Configuration(setup_config_path + ".yaml")
    config.save(setup_config_path + ".bak")

    if os.path.isfile(setup_config_path + ".bak"):
        os.remove(setup_config_path + ".bak")
    else:
        raise Exception("File not found")


def test_load_json(setup_config_path):
    config = Configuration()
    config.load_json(setup_config_path + ".json")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_load_section_json(setup_config_path):
    config = Configuration(setup_config_path + ".json", "api")
    assert config == {"velazquez": "Then I am beautiful?"}


def test_load_yaml(setup_config_path):
    config = Configuration()
    config.load_yaml(setup_config_path + ".yaml")
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
    }


def test_load_section_yaml(setup_config_path):
    config = Configuration(setup_config_path + ".yaml", "devo")
    assert config == {"die": "hard"}


def test_mix_json(setup_config_path):
    config = Configuration(setup_config_path + ".json")
    config.mix({"test": "ok"})
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
        "test": "ok",
    }


def test_mix_yaml(setup_config_path):
    config = Configuration(setup_config_path + ".yaml")
    config.mix({"test": "ok"})
    assert config == {
        "devo": {"die": "hard"},
        "api": {"velazquez": "Then I am beautiful?"},
        "test": "ok",
    }


if __name__ == "__main__":
    pytest.main()
