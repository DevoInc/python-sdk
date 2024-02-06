from pathlib import Path
import unittest
from devo.sender.data import Sender, open_file

# This test case uses the private method __encode_record to test the encoding
# of the records and needs some name mangling to access it.


class TestEncoding(unittest.TestCase):

    def test_encode_record_ascii(self):
        record = 'Hello'  # ASCII Normal sequence
        encoded_record = Sender._Sender__encode_record(record)
        self.assertEqual(encoded_record, b'Hello')

    def test_encode_record_utf8(self):
        record = 'Hello 🌍, こんにちは'  # UTF-8 sequence
        encoded_record = Sender._Sender__encode_record(record)
        self.assertEqual(encoded_record, b'Hello \xf0\x9f\x8c\x8d, \xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf')

    def test_encode_record_utf8_with_byte_sequence(self):
        record = '10 €'  # UTF-8 valid byte sequence
        encoded_record = Sender._Sender__encode_record(record)
        self.assertEqual(encoded_record, b'10 \xe2\x82\xac')

    def test_encode_record_utf16_surrogate(self):
        record = '\uD83D Hello'  # UTF-16 sequence
        encoded_record = Sender._Sender__encode_record(record)
        self.assertEqual(encoded_record, b'? Hello')


if __name__ == "__main__":
    unittest.main()
