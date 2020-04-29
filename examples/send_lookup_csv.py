import os
from devo.sender import Sender, SenderConfigSSL, Lookup

server = "us.elb.relay.logtrust.net"
port = 443
key = os.getenv('DEVO_SENDER_KEY')
cert = os.getenv('DEVO_SENDER_CERT')
chain = os.getenv('DEVO_SENDER_CHAIN')

lookup_name = 'Test_Lookup_Csv'
lookup_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                       os.sep, "example_data", os.sep, "example.csv"))

lookup_key = 'KEY'

engine_config = SenderConfigSSL(address=(server, port),
                                key=key, cert=cert,
                                chain=chain)
con = Sender(engine_config)
lookup = Lookup(name=lookup_name, historic_tag=None, con=con)

with open(lookup_file) as f:
    line = f.readline()

lookup.send_csv(lookup_file,
                headers=line.rstrip().split(","),
                key=lookup_key)

con.close()

