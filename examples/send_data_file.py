import os
from devo.sender import Sender, SenderConfigSSL


server = "us.elb.relay.logtrust.net"
port = 443
key = os.getenv('DEVO_SENDER_KEY')
cert = os.getenv('DEVO_SENDER_CERT')
chain = os.getenv('DEVO_SENDER_CHAIN')


file = "".join((os.path.dirname(os.path.abspath(__file__)),
                os.sep, "example_data", os.sep, "example.csv"))

engine_config = SenderConfigSSL(address=(server, port),
                                key=key, cert=cert,
                                chain=chain)
con = Sender(engine_config)

with open(file) as f:
    for line in f:
        con.send(tag="my.app.sdk.example", msg=line)

con.close()

