import os
from devo.sender import Sender, SenderConfigSSL

server = "us.elb.relay.logtrust.net"
port = 443
key = os.getenv('DEVO_SENDER_KEY')
cert = os.getenv('DEVO_SENDER_CERT')
chain = os.getenv('DEVO_SENDER_CHAIN')

engine_config = SenderConfigSSL(address=(server, port),
                                key=key, cert=cert,
                                chain=chain)
con = Sender(engine_config)

for _ in range(1000):
    con.send(tag="my.app.sdk.example", msg="Hello world", zip=True)

# Its important fill the buffer ever
con.fill_buffer()

con.close()
