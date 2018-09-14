# -*- coding: utf-8 -*-
""" File with utils for send Lookups to Devo """
import time
import sys
import csv
import re
PY3 = sys.version_info[0] > 2


class Lookup:
    """ Main class Lookup for create and send the object from some sources """
    # Type of the header sended
    # - EVENT_START for START header
    # - EVENT_END for END header
    EVENT_START = 'START'
    EVENT_END = 'END'

    # Action of lookup:
    # - FULL replace all data in the lookup for the new one
    # - INC add rows to the lookup base on the key
    ACTION_FULL = 'FULL'
    ACTION_INC = 'INC'

    # Time to wait after send START and before send END
    # This is for avoid sync problem (In most cases not need)
    delay = 5

    def __init__(self, name="example", historic_tag=None,
                 con=None, delay=5):

        if con is None:
            raise Exception('Devo Lookup: Undefined devo sender.')

        self.lookup_id = str(time.time())
        self.con = con
        self.historic_tag = historic_tag
        self.name = name.replace(" ", "_")
        self.delay = delay

    # Helper methods
    # --------------------------------------------------------------------------
    def send_headers(self, headers=None, key="KEY", event='START', action='FULL'):
        """
        Send only the headers
        :param headers:
        :param key:
        :param event:
        :param action:
        :return:
        """
        p_headers = Lookup.list_to_headers(headers, key)
        self.send_control(event, p_headers, action)

    def send_data_line(self, key="key", fields=None, delete=False):
        """
        Send only the data
        :param key:
        :param fields:
        :param delete:
        :return:
        """
        p_fields = Lookup.list_to_fields(fields, key)
        self.send_data(p_fields, delete)

    # Send a whole CSV file
    def send_csv(self, path, has_header=True, delimiter=',', quotechar='"',
                 headers=None, key="KEY", historic_tag=None):
        """Send CSV file to lookup

        :param path: The path to CSV file
        :param has_header: If the file has header to avoid it (default True)
        :param delimiter: CSV delimiter (default ;)
        :param quotechar: CSV quotechar (default ")
        :param headers: List with all headers in the same order as the CSV file,
        :param key: The key Header.
        """
        try:
            with open(path, 'r') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=delimiter,
                                        quotechar=quotechar)

                # Send control START with FULL (parsedHeaders)
                p_headers = Lookup.list_to_headers(headers, key)
                self.send_control(self.EVENT_START, p_headers, self.ACTION_FULL)

                counter = 0

                for fields in spamreader:
                    # Check first header and avoid it
                    if has_header:
                        has_header = False
                        continue

                    # Send data
                    field_key = Lookup.list_extract_key(headers, fields, key)
                    p_fields = Lookup.list_to_fields(fields, field_key)
                    self.send_data(p_fields)

                    # Send full log for historic
                    if historic_tag is not None:
                        self.send_full(historic_tag, ','.join(fields))

                    counter += 1

                # Send control END
                self.send_control(self.EVENT_END, p_headers, self.ACTION_FULL)

                return counter
        except IOError as error:
            print("I/O error({0}): {1}".format(error.errno, error.strerror))
        except Exception as error:
            raise Exception("Unexpected error: %e \n" % error, sys.exc_info()[0])

    # Basic process
    # --------------------------------------------------------------------------
    def send_control(self, event, headers, action):
        """
        Send data to my.lookup.control

        >>>header = Lookup.list_to_headers(headers, "KEY")
        >>>obj.send_start(EVENT_START, header, ACTION_FULL)

        :param type:
        :param headers:
        :param action:
        :return:
        """
        if event == self.EVENT_END:
            time.sleep(self.delay)
        line = "%s_%s|%s|%s" % (self.lookup_id, self.name, event, headers)
        self.con.tag = "my.lookup.control.%s.%s" % (self.name, action)
        self.con.send(self.con.tag, line)
        if event == self.EVENT_START:
            time.sleep(self.delay)

    def send_data(self, row='', delete=False):
        """
        Send data to my.lookup.data

        >>>row = Lookup.list_to_fields(fields, "23")
        >>>obj.send_data(row)
        :param row:
        :param delete:
        :return:
        """
        line = "%s_%s|%s" % (self.lookup_id, self.name, row)
        self.con.tag = "my.lookup.data.%s" % self.name
        if delete:
            self.con.tag += '.DELETE'
        self.con.send(self.con.tag, line)

    def send_full(self, historic_tag, row):
        """
        Send the full log in plain format for maintenance

        >>>obj.send_data(line)
        :param historic_tag:
        :param row:
        :return:
        """
        self.con.tag = historic_tag
        self.con.send(self.con.tag, row)

    # Utils
    # --------------------------------------------------------------------------
    @staticmethod
    def list_extract_key(headers, fields, key):
        """
        Extract the key for the full list
        :param list headers: headers of lookup
        :param list fields: values of the row
        :param str key: key name of the lookup
        :type
        """
        key = key.strip()
        index = 0

        if headers is None:
            return None

        for header in headers:
            if header.strip() == key.strip():
                break
            index += 1
        return fields[index].strip()

    @staticmethod
    def list_to_headers(lst, key, type_of_key="str"):
        """
        Transform list item to the object we need send to Devo for headers

        :param list lst: list of headers names
        :param str key: key name (Must be in lst)
        :param str type_of_key: type of the key field
        :result str:
        """
        # First the key
        out = '[{"%s":{"type":"%s","key":true}}' % (key, type_of_key)
        # The rest of the fields
        if lst is None:
            return out + ']'

        for item in lst:
            # If file is the key don't add
            if item == key:
                continue
            out += ',{"%s":{"type":"str"}}' % item
        out += ']'
        return out

    @staticmethod
    def list_to_fields(lst, key):
        """
        Transform list item to the object we need send to Devo for each row
        :param list lst: list of field names
        :result str
        """
        key = Lookup.clean_field(key)
        # First the key
        out = '%s' % key

        if lst is None:
            return out

        # The rest of the fields
        for item in lst:
            item = Lookup.clean_field(item)
            # If file is the key don't add
            if item == key:
                continue
            out += ',%s' % item
        return out

    @staticmethod
    def clean_field(field):
        """
        Strip and quotechar the fields
        :param str field: field for clean
        :return str: cleaned field
        """
        field = field.strip()
        if not Lookup.is_number(field):
            field = '"%s"' % field
        return field

    @staticmethod
    def is_number(text):
        """
        Check if text is number: int or float

        :param str text: text for evaluate if is a number
        :return bool: Result of regex
        """
        pattern = re.compile(r'^-?\d+((\.\d+)*)$')
        return pattern.match(text)
