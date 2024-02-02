import csv
import io

import pytest

testfile_csv_last_line_is_blank = """key,value1,value2
zzz,yyy,xxx
"""

testfile_csv_with_different_num_fields = """aaa,bbb,ccc
ddd,eee,fff,xxx
ggg,hhh,iii"""

testfile_csv_with_comma_at_eol = """aaa,bbb,ccc
zzz,yyy,xxx,
"""

testfile_csv_with_comma_crlf_in_fields = """aaa,bbb,ccc
zzz,"yy,y",xxx
ddd,"ee
e",fff
"""

testfile_csv_with_quotes = """aaa,bbb,ccc
zzz,"yy""y",xxx
Television,24",LCD
"""

testfile_csv_with_tabs = """aaa\tbbb\tccc
zzz\tyyy\txxx
ddd\teee\tfff
"""

# The Devo SDK Lookup Class uses the CSV reader to read the input lookup file,
# This tests the CSV reader RFC 4180 compliance.
#
# See https://tools.ietf.org/html/rfc4180 for more details.


def test_last_line_is_blank():
    s = io.StringIO(testfile_csv_last_line_is_blank)
    reader = csv.reader(s)
    lines = [row for row in reader]

    assert len(lines) == 2
    assert lines[-1] == ["zzz", "yyy", "xxx"]


@pytest.mark.xfail
def test_same_number_of_fields():
    f = io.StringIO(testfile_csv_with_different_num_fields)
    reader = csv.reader(f)
    lines = [row for row in reader]

    for line in lines:
        assert len(line) == 3


@pytest.mark.xfail
def test_no_comma_at_eol():
    f = io.StringIO(testfile_csv_with_comma_at_eol)
    reader = csv.reader(f)
    lines = [row for row in reader]

    assert lines[0] == ["aaa", "bbb", "ccc"]
    assert lines[1] == ["zzz", "yyy", "xxx"]


def test_fields_with_comma_crlf():
    f = io.StringIO(testfile_csv_with_comma_crlf_in_fields)
    reader = csv.reader(f)
    lines = [row for row in reader]

    # The nomber of lines read should not be the same as the number of
    # lines in the file.
    assert reader.line_num == 4
    assert len(lines) == 3
    assert lines[0] == ["aaa", "bbb", "ccc"]
    assert lines[1] == ["zzz", "yy,y", "xxx"]
    assert lines[2] == ["ddd", "ee\ne", "fff"]


def test_fields_with_quotes():
    f = io.StringIO(testfile_csv_with_quotes)
    reader = csv.reader(f)
    lines = [row for row in reader]

    # The files with quotes inside will be checked by the
    # function that sends the data in the Devo SDK and a warning
    # will be issued, but the reader has to read the file.

    assert len(lines) == 3
    assert lines[0] == ["aaa", "bbb", "ccc"]
    assert lines[1] == ["zzz", 'yy"y', "xxx"]
    assert lines[2] == ["Television", '24"', "LCD"]


def test_fields_with_tabs():
    f = io.StringIO(testfile_csv_with_tabs)
    reader = csv.reader(f, delimiter="\t")
    lines = [row for row in reader]

    assert len(lines) == 3
    assert lines[0] == ["aaa", "bbb", "ccc"]
    assert lines[1] == ["zzz", "yyy", "xxx"]
    assert lines[2] == ["ddd", "eee", "fff"]


if __name__ == "__main__":
    pytest.main()
