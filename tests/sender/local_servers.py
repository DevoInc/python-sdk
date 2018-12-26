import threading
import os
import socket
import ssl
import sys

PY3 = sys.version_info[0] > 2

if not PY3:
    import SocketServer

    class CustomTCPHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            self.data = self.rfile.readline().strip()
            self.wfile.write(self.data.upper())


class SSL_Server:
    def __init__(self, ip="0.0.0.0", port=4488):
        self.shutdown = False
        self.server = None
        self.file_path = "".join((os.path.dirname(os.path.abspath(__file__)),os.sep))
        self.server = threading.Thread(target=self.start_server,
                                       kwargs={'ip': ip, 'port': port})
        self.server.setDaemon(True)
        self.server.start()

    '''
    Implement the SSL SERVER
    '''
    def start_server(self, ip, port):
        sslSocket = socket.socket()
        sslSocket.bind((ip, port))
        sslSocket.listen(5)
        stream = None
        server_cert = os.getenv('DEVO_SENDER_SERVER_CRT', "".join((self.file_path, "local_server_files", os.sep, "server.crt")))
        server_key = os.getenv('DEVO_SENDER_SERVER_KEY', "".join((self.file_path, "local_server_files", os.sep, "server.key")))
        try:
            while not self.shutdown:
                conn, addr = sslSocket.accept()
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
                data = stream.recv(5000)
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


class TCP_Server:
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
        if PY3:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((ip, port))
            s.listen(5)
            conn, addr = s.accept()
            while not self.shutdown:
                data = conn.recv(5000)
                conn.send(data)
        else:
            server = SocketServer.TCPServer((ip, port), CustomTCPHandler)
            server.serve_forever()

    def close_server(self):
        self.shutdown = True
