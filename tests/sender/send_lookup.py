import unittest
from ssl import CERT_NONE
from unittest import mock

from devo.sender import Sender, SenderConfigSSL, Lookup
from .load_certs import *


class TestLookup(unittest.TestCase):
    def setUp(self):
        self.server = os.getenv('DEVO_SENDER_SERVER', "127.0.0.1")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 4488))

        self.key = os.getenv('DEVO_SENDER_KEY', CLIENT_KEY)
        self.cert = os.getenv('DEVO_SENDER_CERT', CLIENT_CERT)
        self.chain = os.getenv('DEVO_SENDER_CHAIN', CLIENT_CHAIN)

        self.lookup_name = 'Test_Lookup_of_today'
        self.lookup_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                                    os.sep, "testfile_lookup.csv"))

        self.lookup_key = 'KEY'

    def test_ssl_lookup_csv_send(self):

        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key, cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE)
        con = Sender(engine_config)
        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)

        with open(self.lookup_file) as f:
            line = f.readline()

        lookup.send_csv(self.lookup_file,
                        headers=line.rstrip().split(","),
                        key=self.lookup_key)

        con.socket.shutdown(0)

    # Add new line to lookup
    def test_ssl_lookup_new_line(self):
        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key, cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        p_headers = Lookup.list_to_headers(['KEY', 'HEX', 'COLOR'], 'KEY')
        lookup.send_control('START', p_headers, 'INC')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"])
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_control('END', p_headers, 'INC')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')

        con.socket.shutdown(0)

    def test_create_lookup_key_index_preserves_structure(self):
        engine_config = SenderConfigSSL(
            address=(self.server, self.port),
            key=self.key,
            cert=self.cert,
            chain=self.chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender(engine_config)
        lookup = Lookup(name=self.lookup_name, con=con)
        headers = ["col1", "col2", "col3"]
        fields = ["a", "b", "c"]

        expected_headers = Lookup.list_to_headers(headers, key_index=0)
        with mock.patch.object(
                lookup, "send_control", wraps=lookup.send_control
        ) as lookup_spy:
            lookup.send_headers(
                headers=headers, key_index=0, event="START", action="FULL"
            )
            lookup_spy.assert_called_with(
                action="FULL", event="START", headers=expected_headers
            )
            lookup.send_data_line(key_index=0, fields=fields)
            lookup.send_headers(
                headers=headers, key_index=0, event="END", action="FULL"
            )
            lookup_spy.assert_called_with(
                action="FULL", event="END", headers=expected_headers
            )

    def test_send_headers_with_type_of_key(self):
        engine_config = SenderConfigSSL(
            address=(self.server, self.port),
            key=self.key,
            cert=self.cert,
            chain=self.chain,
            check_hostname=False,
            verify_mode=CERT_NONE,
        )
        con = Sender(engine_config)
        lookup = Lookup(name=self.lookup_name, con=con)
        headers = ["col1", "col2", "col3"]

        expected_headers = '[{"col1":{"type":"int4","key":true}},{"col2":{"type":"str"}},{"col3":{"type":"str"}}]'
        with mock.patch.object(
                lookup, "send_control", wraps=lookup.send_control
        ) as lookup_spy:
            lookup.send_headers(
                headers=headers, key_index=0, type_of_key="int4", event="START", action="FULL"
            )
            lookup_spy.assert_called_with(
                action="FULL", event="START", headers=expected_headers
            )
        con.socket.shutdown(0)

    # add new line deleting previous data
    def test_ssl_lookup_override(self):
        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key, cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        p_headers = Lookup.list_to_headers(['KEY', 'HEX', 'COLOR'], 'KEY')
        lookup.send_control('START', p_headers, 'FULL')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"])
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_control('END', p_headers, 'FULL')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')

        con.socket.shutdown(0)

    # delete a line from lookup
    def test_ssl_lookup_delete_line(self):
        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key, cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        p_headers = Lookup.list_to_headers(['KEY', 'HEX', 'COLOR'], 'KEY')
        lookup.send_control('START', p_headers, 'INC')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"],
                              delete=True)
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_control('END', p_headers, 'INC')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')

        con.socket.shutdown(0)

    def test_ssl_lookup_simplify(self):
        engine_config = SenderConfigSSL(address=(self.server, self.port),
                                        key=self.key, cert=self.cert,
                                        chain=self.chain,
                                        check_hostname=False,
                                        verify_mode=CERT_NONE)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY',
                            action='START')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"])
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')
        lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY',
                            action='END')
        if len(con.socket.recv(1000)) == 0:
            raise Exception('Not msg sent!')

        con.socket.shutdown(0)

    def test_check_is_number(self):
        self.assertTrue(Lookup.is_number('5'))
        self.assertTrue(Lookup.is_number('5.0'))

    def test_check_is_not_a_number(self):
        self.assertFalse(Lookup.is_number('5551,HNBId=001D4C-1213120051,'
                                            'Fsn=1213120051,bSRName=,'
                                            'manualPscUsed=false'))
        self.assertFalse(Lookup.is_number('5.'))
        self.assertFalse(Lookup.is_number('5,0'))

    def test_process_fields_does_not_modify_arguments(self):
        fields = ["a", "b", "c"]

        processed_fields = Lookup.process_fields(fields, key_index=1)

        self.assertEqual(fields, ["a", "b", "c"])
        self.assertEqual(processed_fields, '"b","a","c"')


if __name__ == '__main__':
    unittest.main()
