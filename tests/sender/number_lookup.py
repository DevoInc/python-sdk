import unittest
from devo.sender import Lookup


class TestLookup(unittest.TestCase):
    def test_check_is_number(self):
        self.assertTrue(Lookup.is_number('5'))
        self.assertTrue(Lookup.is_number('5.0'))

    def test_check_is_not_a_number(self):
        self.assertFalse(Lookup.is_number('5551,HNBId=001D4C-1213120051,'
                                            'Fsn=1213120051,bSRName=,'
                                            'manualPscUsed=false'))
        self.assertFalse(Lookup.is_number('5.'))
        self.assertFalse(Lookup.is_number('5,0'))


if __name__ == '__main__':
    unittest.main()
