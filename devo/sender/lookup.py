# -*- coding: utf-8 -*-
""" File with utils for send Lookups to Devo """
import time
import sys
import csv
import re


def find_key_index(value=None, headers=None):
    """Find index of key value in a list"""
    for index, val in enumerate(headers):
        if val == value:
            yield index


def find_delete_index(value=None, headers=None):
    """Find index of action value in a list"""
    for index, val in enumerate(headers):
        if val == value:
            yield index


class Lookup:
    """ Main class Lookup for create and send the object from some sources """
    # Type of the header sent
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

    # Tables to send lookups
    DATA_TABLE = "my.lookup.data"
    CONTROL_TABLE = "my.lookup.control"

    def __init__(self, name="example", historic_tag=None,
                 con=None, delay=5):

        if not re.match(r"^[A-Za-z0-9_]+$", name):
            raise Exception('Devo Lookup: The name of the lookup is incorrect,'
                            ' must contain only letters, '
                            'numbers and underscore')

        if con is None:
            raise Exception('Devo Lookup: Undefined devo sender.')

        self.lookup_id = str(time.time())
        self.con = con
        self.historic_tag = historic_tag
        self.name = name.replace(" ", "_")
        self.delay = delay

    # Helper methods
    # --------------------------------------------------------------------------
    def send_headers(self, headers=None, key="KEY", event='START',
                     action='FULL', types=None, key_index=None):
        """
        Send only the headers
        :param headers: list with headers names
        :param key: key value, optional if you send 'key_index'
        :param key_index: index of key in headers. Optional if you send 'key'
        :param event: START or END
        :param action: FULL or INC to send new full lookup or for update one
        :param types: dict with types of each header
        :return:
        """
        p_headers = Lookup.list_to_headers(headers=headers, key=key,
                                           types=types, key_index=key_index)
        self.send_control(event=event, headers=p_headers, action=action)

    def send_data_line(self, key=None, fields=None,
                       delete=False, key_index=None):
        """
        Send only the data
        :param key: key value, optional if you send 'key_index'
        :param key_index: index of key in headers. Optional if you send 'key'
        :param fields: list with fields values
        :param delete: action for field: 'delete' to delete field with this key
                       or add to add value
        :return:
        """
        # TODO: Deprecate this if with list_to_fields in v4
        p_fields = Lookup.list_to_fields(fields=fields, key=key) \
            if key_index is None \
            else Lookup.process_fields(fields=fields, key_index=key_index)
        self.send_data(row=p_fields, delete=delete)

    @staticmethod
    def detect_types(reader=None):
        """
        Function to detect types of each column
        :param reader: CSV Reader iterator
        :return:
        """
        reader.__next__()
        line = reader.__next__()

        types = dict()
        for index, item in enumerate(line):
            types[index] = None
            try:
                int(item)
                types[index] = "int"
            except ValueError:
                pass

            if not types[index]:
                try:
                    float(item)
                    types[index] = "float"
                except ValueError:
                    pass

            if not types[index]:
                try:
                    ip_regex = re.compile(
                        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
                    )
                    result = ip_regex.match(item)
                    if result is not None:
                        types[index] = "ip4"
                except Exception:
                    pass

            if types[index] is None:
                types[index] = "str"
        return types

    # Send a whole CSV file
    def send_csv(self, path=None, has_header=True, delimiter=',',
                 quotechar='"', headers=None, key="KEY", historic_tag=None,
                 action="FULL", delete_field=None,
                 types=None, detect_types=False):
        """Send CSV file to lookup

        :param path: The path to CSV file
        :param has_header: If the file has header to avoid it (default True)
        :param delimiter: CSV delimiter (default ;)
        :param quotechar: CSV quotechar (default ")
        :param headers: List with all headers in the same order as the CSV file
        :param historic_tag: .
        :param action: FULL or INC
        :param key: The key name in Headers.
        :param delete_field: The delete_field name in Headers.
        :param types: Dict with types of headers.
        :param detect_types: True or False for autodetect types of each column
        """
        try:
            if detect_types:
                with open(path, 'r') as csv_file:
                    spam_reader = csv.reader(csv_file, delimiter=delimiter,
                                             quotechar=quotechar)

                    types = self.detect_types(reader=spam_reader)
        except IOError as error:
            print("I/O error({0}): {1}".format(error.errno, error.strerror))
        except Exception as error:
            raise Exception("Unexpected error: %e \n" % error,
                            sys.exc_info()[0])

        try:
            with open(path, 'r') as csv_file:
                spam_reader = csv.reader(csv_file, delimiter=delimiter,
                                         quotechar=quotechar)
                # Conform headers list
                if has_header is False and headers is None:
                    raise Exception("No headers for fields")
                elif has_header is True:
                    headers = spam_reader.__next__()
                elif not isinstance(headers, list):
                    headers = headers.split(delimiter)

                this_action = self.ACTION_INC if action == "INC" \
                    else self.ACTION_FULL
                counter = 0

                # Find key index
                key_index = find_key_index(key, headers).__next__()
                try:
                    delete_index = find_delete_index(delete_field,
                                                     headers).__next__()
                    del headers[delete_index]
                except StopIteration:
                    delete_index = None

                # Send control START with ACTION (parsedHeaders)
                p_headers = Lookup.list_to_headers(headers=headers,
                                                   key_index=key_index,
                                                   types=types)

                self.send_control(self.EVENT_START, p_headers, this_action)

                if delete_index is not None:
                    for fields in spam_reader:
                        field_action = fields.pop(delete_index)
                        p_fields = Lookup.process_fields(fields=fields,
                                                         key_index=key_index)
                        self.send_data(row=p_fields,
                                       delete=field_action == "delete"
                                       or field_action == "DELETE")

                        # Send full log for historic
                        if historic_tag is not None:
                            self.send_full(historic_tag, ','.join(fields))
                        counter += 1
                else:
                    for fields in spam_reader:
                        p_fields = Lookup.process_fields(fields=fields,
                                                         key_index=key_index)
                        self.send_data(row=p_fields)

                        # Send full log for historic
                        if historic_tag is not None:
                            self.send_full(historic_tag, ','.join(fields))
                        counter += 1

                # Send control END
                self.send_control(self.EVENT_END, p_headers, this_action)
                return counter
        except IOError as error:
            print("I/O error({0}): {1}".format(error.errno, error.strerror))
        except Exception as error:
            raise Exception("Unexpected error: %e \n" % error, sys.exc_info()[0])

    # Basic process
    # --------------------------------------------------------------------------
    def send_control(self, event=None, headers=None, action=None):
        """
        Send data to table of lookup control data

        >>>header = Lookup.list_to_headers(headers, "KEY")
        >>>obj.send_start(EVENT_START, header, ACTION_FULL)

        :param event: event to send
        :param headers: header (list) names
        :param action: action, can be START or END
        :return:
        """
        if event == self.EVENT_END:
            time.sleep(self.delay)
        line = "%s_%s|%s|%s" % (self.lookup_id, self.name, event, headers)
        self.con.tag = "%s.%s.%s" % (self.CONTROL_TABLE, self.name, action)
        self.con.send(self.con.tag, line)
        if event == self.EVENT_START:
            time.sleep(self.delay)

    def send_data(self, row='', delete=False):
        """
        Send data to table of lookup data

        >>>row = Lookup.list_to_fields(fields, "23")
        >>>obj.send_data(row)
        :param row: row to send
        :param delete: True or False. Its true, delete row with same key
        :return:
        """
        line = "%s_%s|%s" % (self.lookup_id, self.name, row)
        self.con.tag = "%s.%s" % (self.DATA_TABLE, self.name)
        if delete:
            self.con.tag += '.DELETE'
        return self.con.send(tag=self.con.tag, msg=line)

    def send_full(self, historic_tag=None, row=None):
        """
        Send the full log in plain format for maintenance
        :param historic_tag: tag to send logs
        :param row: row to send to Devo
        :return:
        """
        self.con.tag = historic_tag
        self.con.send(tag=self.con.tag, msg=row)

    # Utils
    # --------------------------------------------------------------------------
    # TODO: Deprecated
    @staticmethod
    def list_extract_key(headers=None, fields=None, key=None):
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
    def list_to_headers(headers=None, key=None,
                        type_of_key="str",
                        key_index=None,
                        types=None):
        """
        Transform list item to the object we need send to Devo for headers

        :param list headers: list of headers names
        :param str key: key name (Must be in headers)
        :param str type_of_key: type of the key field
        :result str:
        """
        # First the key
        if key is not None:
            out = '[{"%s":{"type":"%s","key":true}}' % (key, types[key_index]
                                                        if types
                                                        else type_of_key)
        elif key_index is not None:
            key = headers[key_index]
            out = '[{"%s":{"type":"%s","key":true}}' % (key,
                                                        types[key_index]
                                                        if types
                                                        else type_of_key)
        else:
            raise Exception("Not key identified")

        # The rest of the fields
        if headers is None:
            return out + ']'
        aux = -1
        for item in headers:
            aux += 1
            # If file is the key don't add
            if item == key:
                continue
            field_type = "str" if not isinstance(types, dict) else types[aux]
            out += ',{"%s":{"type":"%s"}}' % (item, field_type)
        out += ']'
        return out

    @staticmethod
    def field_to_str(field):
        """
        Convert one value to STR, cleaning it
        :param field: field to clean
        :return:
        """
        return ',%s' % Lookup.clean_field(field)

    @staticmethod
    def process_fields(fields=None, key_index=None):
        """
        Method to convert list with one row/fields to STR to send
        :param fields: fields list
        :param key_index: index of key in fields
        :return:
        """
        # First the key
        out = '%s' % Lookup.clean_field(fields.pop(key_index))

        # The rest of the fields
        for item in fields:
            out += Lookup.field_to_str(item)
        return out

    # TODO: Deprecated
    @staticmethod
    def list_to_fields(fields=None, key="key"):
        """
        Transform list item to the object we need send to Devo for each row
        :param list fields: list of field names
        :param str key: key name, optional
        :result str
        """
        key = Lookup.clean_field(key)
        # First the key
        out = '%s' % key

        if fields is None:
            return out

        # The rest of the fields
        for item in fields:
            item = Lookup.clean_field(item)
            # If file is the key don't add
            if item == key:
                continue
            out += ',%s' % item
        return out

    @staticmethod
    def clean_field(field=None):
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
    def is_number(text=""):
        """
        Check if text is number: int or float

        :param str text: text for evaluate if is a number
        :return bool: Result of regex
        """
        pattern = re.compile(r'^-?\d+((\.\d+)*)$')
        return pattern.match(text)
