import os

from devo.sender import Lookup, Sender, SenderConfigSSL

server = "collector-us.devo.io"
port = 443
key = os.getenv("DEVO_SENDER_KEY")
cert = os.getenv("DEVO_SENDER_CERT")
chain = os.getenv("DEVO_SENDER_CHAIN")

lookup_name = "Test_Lookup_Line_By_Line"

engine_config = SenderConfigSSL(address=(server, port), key=key, cert=cert, chain=chain)
con = Sender(engine_config)
lookup = Lookup(name=lookup_name, historic_tag=None, con=con)

p_headers = Lookup.list_to_headers(["KEY", "HEX", "COLOR"], "KEY")
lookup.send_control("START", p_headers, "INC")

lookup.send_data_line(key_index=0, fields=["22", "HEX22_NEW", "COLOR22_NEW"])
lookup.send_data_line(key_index=0, fields=["44", "HEX44", "COLOR44"])

lookup.send_control("END", p_headers, "INC")

con.close()
