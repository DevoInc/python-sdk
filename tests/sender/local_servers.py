import threading
import os
import socket
import ssl


class SSLServer:
    def __init__(self, ip="0.0.0.0", port=4488):
        self.shutdown = False
        self.server = None
        self.file_path = "".join((os.path.dirname(os.path.abspath(__file__)),
                                  os.sep))
        self.server = threading.Thread(target=self.start_server,
                                       kwargs={'ip': ip, 'port': port})
        self.server.setDaemon(True)
        self.server.start()

    '''
    Implement the SSL SERVER
    '''
    def start_server(self, ip, port):
        ssl_socket = socket.socket()
        ssl_socket.bind((ip, port))
        ssl_socket.listen(10)
        stream = None

        server_cert = os.getenv('DEVO_SENDER_SERVER_CRT',
                                "{!s}local_certs/keys/server/server_cert.pem"
                                .format(self.file_path))

        server_key = os.getenv('DEVO_SENDER_SERVER_KEY',
                               "{!s}local_certs/keys/server/"
                               "private/server_key.pem"
                               .format(self.file_path))
        try:
            while not self.shutdown:
                conn, addr = ssl_socket.accept()
                stream = ssl.wrap_socket(conn, server_side=True,
                                         certfile=server_cert,
                                         keyfile=server_key)
                stream.settimeout(15)
                self.connect_client(stream)
        finally:
            if stream:
                stream.close()

    '''
    Read stream
    '''
    def connect_client(self, stream):
        try:
            while not self.shutdown:
                data = stream.recv(8000)
                stream.send(data)
        except socket.timeout:
            print("Timeout")
        except ssl.SSLEOFError:
            print("Socket closed by client when recv")
        except Exception as error:
            print("Other exception")
            print(type(error))
            print(error)

    def close_server(self):
        self.shutdown = True


class TCPServer:
    def __init__(self, ip="0.0.0.0", port=4489):
        self.shutdown = False
        self.server = None
        self.file_path = "".join((os.path.dirname(os.path.abspath(__file__)),
                                  os.sep))
        self.server = threading.Thread(target=self.start_server,
                                       kwargs={'ip': ip, 'port': port})
        self.server.setDaemon(True)
        self.server.start()

    def start_server(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        s.listen(5)
        conn, addr = s.accept()
        while not self.shutdown:
            data = conn.recv(8000)
            conn.send(data)

    def close_server(self):
        self.shutdown = True
