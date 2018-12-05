import os

CLIENT_KEY = "".join((os.path.dirname(os.path.abspath(__file__)),
                      os.sep, 'local_server_files', os.sep, 'client.key'))
CLIENT_CERT = "".join((os.path.dirname(os.path.abspath(__file__)),
                       os.sep, 'local_server_files', os.sep, 'client.crt'))
CLIENT_CHAIN = "".join((os.path.dirname(os.path.abspath(__file__)),
                        os.sep, 'local_server_files', os.sep, 'ca.crt'))
