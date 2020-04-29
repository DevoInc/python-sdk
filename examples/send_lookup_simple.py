import os
from devo.sender import Sender, SenderConfigSSL, Lookup

server = "us.elb.relay.logtrust.net"
port = 443
key = os.getenv('DEVO_SENDER_KEY')
cert = os.getenv('DEVO_SENDER_CERT')
chain = os.getenv('DEVO_SENDER_CHAIN')

lookup_name = 'Test_Lookup_Line_By_Line'

engine_config = SenderConfigSSL(address=(server, port),
                                key=key, cert=cert,
                                chain=chain)
con = Sender(engine_config)
lookup = Lookup(name=lookup_name, historic_tag=None, con=con)

p_headers = Lookup.list_to_headers(['KEY', 'HEX', 'COLOR'], 'KEY')
lookup.send_control('START', p_headers, 'FULL')

lookup.send_data_line(key="11", fields=["11", "HEX11", "COLOR11"])
lookup.send_data_line(key="22", fields=["22", "HEX22", "COLOR22"])
lookup.send_data_line(key="33", fields=["33", "HEX33", "COLOR33"])

lookup.send_control('END', p_headers, 'FULL')

con.close()
