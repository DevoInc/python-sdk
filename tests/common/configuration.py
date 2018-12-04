import unittest
import os
from devo.common import Configuration


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.config_path = "%s%stestfile_config" % \
                           (os.path.dirname(os.path.abspath(__file__)), os.sep)

    def test_load_config(self):
        config = Configuration()
        with self.assertRaises(Exception) as context:
            config.load_config(self.config_path + ".ini")

        self.assertTrue("Configuration file type unknown or not supportted: %s%stestfile_config.ini" % \
                        (os.path.dirname(os.path.abspath(__file__)), os.sep) in str(context.exception))

    def test_load_json(self):
        config = Configuration()
        config.load_config(self.config_path + ".json")
        self.assertDictEqual(config.cfg, {"devo": {
            "die": "hard"
        },
            "api": {
                "velazquez": "Then I am beautiful?"
            }
        })

    def test_load_section_json(self):
        config = Configuration()
        config.load_config(self.config_path + ".json", "api")
        self.assertDictEqual(config.cfg, {"velazquez": "Then I am beautiful?"})

    def test_load_yaml(self):
        config = Configuration()
        config.load_config(self.config_path + ".yaml")
        self.assertDictEqual(config.cfg, {"devo": {
            "die": "hard"
        },
            "api": {
                "velazquez": "Then I am beautiful?"
            }
        })

    def test_load_section_yaml(self):
        config = Configuration()
        config.load_config(self.config_path + ".yaml", "devo")
        self.assertDictEqual(config.cfg, {"die": "hard"})

    def test_mix_json(self):
        config = Configuration()
        config.load_config(self.config_path + ".json")
        config.mix({"test": "ok"})
        self.assertDictEqual(config.cfg, {"devo": {
            "die": "hard"
        },
            "api": {
                "velazquez": "Then I am beautiful?"
            },
            "test": "ok"
        })

    def test_mix_yaml(self):
        config = Configuration()
        config.load_config(self.config_path + ".yaml")
        config.mix({"test": "ok"})
        self.assertDictEqual(config.cfg, {"devo": {
            "die": "hard"
        },
            "api": {
                "velazquez": "Then I am beautiful?"
            },
            "test": "ok"
        })

    def test_key_exist(self):
        config = Configuration()
        config.load_config(self.config_path + ".json")
        self.assertFalse(config.key_exist("noexiste"))
        self.assertTrue(config.key_exist("api"))


if __name__ == '__main__':
    unittest.main()