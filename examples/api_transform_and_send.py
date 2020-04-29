import os
from devo.api import Client, ClientConfig, SIMPLECOMPACT_TO_OBJ
from devo.sender import Sender, SenderConfigSSL

key = os.getenv('DEVO_API_KEY', None)
secret = os.getenv('DEVO_API_SECRET', None)

api = Client(auth={"key": key, "secret": secret},
             address="https://apiv2-eu.devo.com/search/query",
             config=ClientConfig(response="json/simple/compact",
                                 stream=True, processor=SIMPLECOMPACT_TO_OBJ))


response = api.query(query="from demo.ecommerce.data select *",
                     dates={'from': "today()-1*day()", 'to': "today()"})


server = "us.elb.relay.logtrust.net"
port = 443
key = os.getenv('DEVO_SENDER_KEY')
cert = os.getenv('DEVO_SENDER_CERT')
chain = os.getenv('DEVO_SENDER_CHAIN')

engine_config = SenderConfigSSL(address=(server,port),
                                key=key, cert=cert,
                                chain=chain)
con = Sender(engine_config)

for item in response:
    con.send(tag="my.app.sdk.api",
             msg="{!s} - {!s}".format(item.get("eventdate"),
                                      item.get("method")))

con.close()

