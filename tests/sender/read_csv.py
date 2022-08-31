import csv
import os
from sre_constants import ASSERT
import unittest

test_directory = '.'

testfile_csv_last_line_is_blank = \
    """key,value1,value2
zzz,yyy,xxx
"""

testfile_csv_with_different_num_fields = \
    """aaa,bbb,ccc
ddd,eee,fff,xxx
ggg,hhh,iii"""

testfile_csv_with_comma_at_eol = \
    """aaa,bbb,ccc
zzz,yyy,xxx,
"""

testfile_csv_with_comma_crlf_in_fields = \
    """aaa,bbb,ccc
zzz,"yy,y",xxx
ddd,"ee
e",fff
"""

testfile_csv_with_quotes = \
    """aaa,bbb,ccc
zzz,"yy""y",xxx
ddd,eee",fff
"""

testfile_csv_with_tabs = \
    """aaa\tbbb\tccc
zzz\tyyy\txxx
ddd\teee\tfff
"""

# The Devo SDK Lookup Class uses the CSV reader to read the input lookup file,
# This tests the CSV reader RFC 4180 compliance.
#
# See https://tools.ietf.org/html/rfc4180 for more details.


class TestCSVRFC(unittest.TestCase):
    """Test the CSV RFC compliance."""

    def setUp(self):
        """Set up the module."""

        global test_directory
        # Get file directory.
        test_directory = os.path.dirname(os.path.realpath(__file__))
        os.chdir(test_directory)

        # Create the test files.
        with open('testfile_csv_last_line_is_blank.yaml', 'w') as f:
            f.write(testfile_csv_last_line_is_blank)

        with open('testfile_csv_with_different_num_fields.yaml', 'w') as f:
            f.write(testfile_csv_with_different_num_fields)

        with open('testfile_csv_with_comma_at_eol.yaml', 'w') as f:
            f.write(testfile_csv_with_comma_at_eol)

        with open('testfile_csv_with_comma_crlf_in_fields.yaml', 'w') as f:
            f.write(testfile_csv_with_comma_crlf_in_fields)

        with open('testfile_csv_with_quotes.yaml', 'w') as f:
            f.write(testfile_csv_with_quotes)

        with open('testfile_csv_with_tabs.yaml', 'w') as f:
            f.write(testfile_csv_with_tabs)

    def tearDown(self):
        """Tear down the module."""

        # Cleanup the test files.
        global test_directory
        os.chdir(test_directory)
        for f in [
                'testfile_csv_last_line_is_blank.yaml',
                'testfile_csv_with_different_num_fields.yaml',
                'testfile_csv_with_comma_at_eol.yaml',
                'testfile_csv_with_comma_crlf_in_fields.yaml',
                'testfile_csv_with_quotes.yaml',
                'testfile_csv_with_tabs.yaml'
        ]:
            if os.path.exists(f):
                os.remove(f)

    def test_last_line_is_blank(self):
        with open('testfile_csv_last_line_is_blank.yaml', 'r') as f:
            reader = csv.reader(f)
            lines = [row for row in reader]

        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[-1], ['zzz', 'yyy', 'xxx'])

    @unittest.expectedFailure
    def test_same_number_of_fields(self):
        with open('testfile_csv_with_different_num_fields.yaml', 'r') as f:
            reader = csv.reader(f)
            lines = [row for row in reader]

        for line in lines:
            self.assertEqual(len(line), 3)

    @unittest.expectedFailure
    def test_no_comma_at_eol(self):
        with open('testfile_csv_with_comma_at_eol.yaml', 'r') as f:
            reader = csv.reader(f)
            lines = [row for row in reader]

        self.assertEqual(lines[0], ['aaa', 'bbb', 'ccc'])
        self.assertEqual(lines[1], ['zzz', 'yyy', 'xxx'])

    def test_fields_with_comma_crlf(self):
        with open('testfile_csv_with_comma_crlf_in_fields.yaml', 'r') as f:
            reader = csv.reader(f)
            lines = [row for row in reader]

        # The nomber of lines read should not be the same as the number of 
        # lines in the file.
        self.assertEqual(reader.line_num, 4)
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], ['aaa', 'bbb', 'ccc'])
        self.assertEqual(lines[1], ['zzz', 'yy,y', 'xxx'])
        self.assertEqual(lines[2], ['ddd', 'ee\ne', 'fff'])

    def test_fields_with_quotes(self):
        with open('testfile_csv_with_quotes.yaml', 'r') as f:
            reader = csv.reader(f)
            lines = [row for row in reader]

        # The files with quotes inside will be checked by the
        # function that sends the data in the Devo SDK and a warning
        # will be issued, but the reader has to read the file.

        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], ['aaa', 'bbb', 'ccc'])
        self.assertEqual(lines[1], ['zzz', 'yy"y', 'xxx'])
        self.assertEqual(lines[2], ['ddd', 'eee"', 'fff'])

    def test_fields_with_tabs(self):
        with open('testfile_csv_with_tabs.yaml', 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            lines = [row for row in reader]

        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], ['aaa', 'bbb', 'ccc'])
        self.assertEqual(lines[1], ['zzz', 'yyy', 'xxx'])
        self.assertEqual(lines[2], ['ddd', 'eee', 'fff'])


if __name__ == '__main__':
    unittest.main()
