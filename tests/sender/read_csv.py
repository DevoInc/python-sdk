import csv
import os
import unittest


test_directory = "."

testfile_csv_last_line_is_blank = [
    "key,value1,value2\n",
    "zzz,yyy,xxx\n"
]

testfile_csv_with_different_num_fields = [
    "aaa,bbb,ccc\n",
    "ddd,eee,fff,xxx\n",
    "ggg,hhh,iii"
]

testfile_csv_with_comma_at_eol = [
    "aaa,bbb,ccc\n",
    "zzz,yyy,xxx,\n"
]

testfile_csv_with_comma_crlf_in_fields = [
    'aaa,bbb,ccc\n',
    'zzz,"yy,y",xxx\n',
    'ddd,"ee\ne",fff\n'
]


# The Devo SDK Lookup Class uses the CSV reader to read the input lookup file,
# This tests the CSV reader RFC 4180 compliance.
#
# See https://tools.ietf.org/html/rfc4180 for more details.


class TestCSVRFC(unittest.TestCase):
    """Test the CSV RFC compliance."""

    def test_last_line_is_blank(self):
        lines = [row for row in csv.reader(testfile_csv_last_line_is_blank)]
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[-1], ["zzz", "yyy", "xxx"])

    @unittest.expectedFailure
    def test_same_number_of_fields(self):
        lines = [
            row for row in csv.reader(testfile_csv_with_different_num_fields)]
        for line in lines:
            self.assertEqual(len(line), 3)

    @unittest.expectedFailure
    def test_no_comma_at_eol(self):
        lines = [row for row in csv.reader(testfile_csv_with_comma_at_eol)]
        self.assertEqual(lines[0], ["aaa", "bbb", "ccc"])
        self.assertEqual(lines[1], ["zzz", "yyy", "xxx"])

    def test_fields_with_comma_crlf_quote(self):
        reader = csv.reader(testfile_csv_with_comma_crlf_in_fields)
        lines = [row for row in reader]

        self.assertEqual(reader.line_num, 3)
        self.assertEqual(lines[0], ["aaa", "bbb", "ccc"])
        self.assertEqual(lines[1], ["zzz", "yy,y", "xxx"])
        self.assertEqual(lines[2], ["ddd", "ee\ne", "fff"])


if __name__ == "__main__":
    unittest.main()
