import threading
import socket
import asyncio
import multiprocessing
import os
import ssl


class SSLServer:
    ip = "127.0.0.1"
    port = 4488

    def __init__(self):
        self.shutdown = False
        self.file_path = "".join((os.path.dirname(os.path.abspath(__file__)),
                                  os.sep))
        self.loop = asyncio.get_event_loop()
        self.server_process = multiprocessing.Process(target=self.server,
                                                      name='sslserver')
        self.server_process.start()

    def server(self):
        @asyncio.coroutine
        def handle_connection(reader, writer):
            addr = writer.get_extra_info('peername')
            try:
                while True:
                    data = yield from reader.read(500)
                    print("Server received {!r} from {}".format(data, addr))
                    assert len(data) > 0, repr(data)
                    writer.write(data)
                    yield from writer.drain()
            except Exception:
                writer.close()

        server_cert = os.getenv('DEVO_SENDER_SERVER_CRT',
                                "{!s}local_certs/keys/server/server_cert.pem"
                                .format(self.file_path))

        server_key = os.getenv('DEVO_SENDER_SERVER_KEY',
                               "{!s}local_certs/keys/server/"
                               "private/server_key.pem"
                               .format(self.file_path))

        sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sc.load_cert_chain(server_cert, server_key)

        coro = asyncio.start_server(handle_connection, self.ip, self.port,
                                    ssl=sc, loop=self.loop)
        server = self.loop.run_until_complete(coro)

        print('Serving on {}'.format(server.sockets[0].getsockname()))
        self.loop.run_forever()

    def close_server(self):
        self.shutdown = True
        self.loop.stop()
        self.server_process.terminate()
        self.server_process.join()


class TCPServer:
    def __init__(self, ip="127.0.0.1", port=4489):
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
