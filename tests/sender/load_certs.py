import os

file_path = os.path.dirname(os.path.abspath(__file__))
CLIENT_KEY = "{!s}/local_certs/keys/client/private/client_key.pem".format(file_path)
CLIENT_CERT = "{!s}/local_certs/keys/client/client_cert.pem".format(file_path)
CLIENT_CHAIN = "{!s}/local_certs/keys/ca/ca_cert.pem".format(file_path)
