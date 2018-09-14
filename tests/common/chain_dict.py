import unittest
from devo.common import ChainDict


class TestChainDict(unittest.TestCase):
    def setUp(self):
        self.test_dict = {'film': "Kung Fury", 'disc': {'type': 'dvd'}}
        self.test_values = [['film', 'Kung Fury'], [['disc', 'type'], 'dvd']]

    def test_set_key_chain(self):
        self.assertDictEqual({'one': {'two': 'yes'}},
                             ChainDict.set_key_chain(dict(),
                                                     ['one', 'two'],
                                                     'yes'))

    def test_set_key(self):
        t = ChainDict()
        for item in self.test_values:
            t.set_key(item[0], item[1])
        self.assertDictEqual(self.test_dict, t)


if __name__ == '__main__':
    unittest.main()
