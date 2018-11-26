import unittest
import os
from devo.common import Configuration


class TestConfiguration(unittest.TestCase):
    def setUp(self):
        self.config_path = "%s%stestfile_config.json" % \
                           (os.path.dirname(os.path.abspath(__file__)), os.sep)

    def test_load_json(self):
        config = Configuration()
        config.load_json(self.config_path)
        self.assertDictEqual(config.cfg, {"devo": {
                                         "die": "hard"
                                     },
                                     "api": {
                                         "velazquez": "Then I am beautiful?"
                                      }
        })

    def test_mix(self):
        config = Configuration()
        config.load_json(self.config_path)
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
        config.load_json(self.config_path)
        self.assertFalse(config.key_exist("noexiste"))
        self.assertTrue(config.key_exist("api"))


if __name__ == '__main__':
    unittest.main()
