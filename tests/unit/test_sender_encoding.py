import pytest

from devo.sender.data import Sender

# This test case uses the private method __encode_record to test the encoding
# of the records and needs some name mangling to access it.


def test_encode_record_ascii():
    record = "Hello"  # ASCII
    encoded_record = Sender._Sender__encode_record(record)
    assert encoded_record == b"Hello"


def test_encode_record_utf8():
    record = "10 €"  # UTF-8
    encoded_record = Sender._Sender__encode_record(record)
    assert encoded_record == b"10 \xe2\x82\xac"


def test_encode_record_utf8_with_emoji_and_japanese():
    record = "Hello 🌍, こんにちは"  # UTF-8
    encoded_record = Sender._Sender__encode_record(record)
    assert (
        encoded_record
        == b"Hello \xf0\x9f\x8c\x8d, \xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf"
    )


def test_encode_record_utf16_surrogate():
    record = "\ud83d Hello"  # UTF-16
    encoded_record = Sender._Sender__encode_record(record)
    assert encoded_record == b"? Hello"


if __name__ == "__main__":
    pytest.main([__file__])
