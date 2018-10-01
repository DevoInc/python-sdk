import unittest
import os
from devo.sender import Sender, SenderConfigSSL, Lookup


class TestLookup(unittest.TestCase):
    def setUp(self):
        self.server = os.getenv('DEVO_SENDER_SERVER',
                                "eu.elb.relay.logtrust.net")
        self.port = int(os.getenv('DEVO_SENDER_PORT', 443))

        self.key = os.getenv('DEVO_SENDER_KEY', None)
        self.cert = os.getenv('DEVO_SENDER_CERT', None)
        self.chain = os.getenv('DEVO_SENDER_CHAIN', None)

        self.lookup_name = 'Test_Lookup_of_today'
        self.lookup_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                                    os.sep, "testfile_lookup.csv"))

        self.lookup_key = 'KEY'

    def test_ssl_lookup_csv_send(self):

        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                        key=self.key, cert=self.cert,
                                        chain=self.chain)
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
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                        key=self.key, cert=self.cert,
                                        chain=self.chain)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        p_headers = Lookup.list_to_headers(['KEY', 'HEX', 'COLOR'], 'KEY')
        lookup.send_control('START', p_headers, 'INC')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"])
        lookup.send_control('END', p_headers, 'INC')

        con.socket.shutdown(0)

    # add new line deleting previous data
    def test_ssl_lookup_override(self):
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                        key=self.key, cert=self.cert,
                                        chain=self.chain)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        p_headers = Lookup.list_to_headers(['KEY', 'HEX', 'COLOR'], 'KEY')
        lookup.send_control('START', p_headers, 'FULL')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"])
        lookup.send_control('END', p_headers, 'FULL')

        con.socket.shutdown(0)

    # delete a line from lookup
    def test_ssl_lookup_delete_line(self):
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                        key=self.key, cert=self.cert,
                                        chain=self.chain)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        p_headers = Lookup.list_to_headers(['KEY', 'HEX', 'COLOR'], 'KEY')
        lookup.send_control('START', p_headers, 'INC')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"], delete=True)
        lookup.send_control('END', p_headers, 'INC')

        con.socket.shutdown(0)

    def test_ssl_lookup_simplify(self):
        engine_config = SenderConfigSSL(address=self.server, port=self.port,
                                        key=self.key, cert=self.cert,
                                        chain=self.chain)
        con = Sender(engine_config)

        lookup = Lookup(name=self.lookup_name, historic_tag=None, con=con)
        lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY',
                            action='START')
        lookup.send_data_line(key="11", fields=["11", "HEX12", "COLOR12"])
        lookup.send_headers(headers=['KEY', 'HEX', 'COLOR'], key='KEY',
                            action='END')

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


if __name__ == '__main__':
    unittest.main()
