import asyncio
import multiprocessing
import os
import socket
import ssl
import threading
import time


def find_available_port(address, starting_port):
    """Find an available port to use for the test server."""
    port = starting_port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((address, port))
                return port
        except OSError:
            port += 1


def wait_for_ready_server(address, port):
    num_tries = 3

    while num_tries > 0:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((address, port))
            sock.close()
            break
        except socket.error:
            num_tries -= 1
            time.sleep(1)


class SSLServer:

    def __init__(self, ip="127.0.0.1", port=4488, certfile=None, keyfile=None):
        self.ip = ip
        self.port = port
        self.cert = certfile
        self.key = keyfile
        self.shutdown = False
        self.file_path = "".join((os.path.dirname(os.path.abspath(__file__)), os.sep))
        self.server_process = multiprocessing.Process(target=self.server, name="sslserver")
        self.server_process.start()

    def server(self):

        @asyncio.coroutine
        def handle_connection(reader, writer):
            addr = writer.get_extra_info("peername")
            try:
                while True:
                    data = yield from reader.read(500)
                    print("Server received {!r} from {}".format(data, addr))
                    assert len(data) > 0, repr(data)
                    writer.write(data)
                    yield from writer.drain()
            except Exception:
                writer.close()

        sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sc.load_cert_chain(self.cert, self.key)

        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(handle_connection, self.ip, self.port, ssl=sc, loop=loop)
        server = loop.run_until_complete(coro)

        print("Serving on {}".format(server.sockets[0].getsockname()))
        loop.run_forever()

    def close_server(self):
        self.shutdown = True
        self.server_process.terminate()
        self.server_process.join()


class TCPServer:

    def __init__(self, ip="127.0.0.1", port=4489):
        self.ip = ip
        self.port = port
        self.shutdown = False
        self.server = None
        self.file_path = "".join((os.path.dirname(os.path.abspath(__file__)), os.sep))
        self.server = threading.Thread(target=self.start_server, kwargs={"ip": ip, "port": port})
        self.server.setDaemon(True)
        self.server.start()

    def start_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.ip, self.port))
        s.listen(5)
        conn, addr = s.accept()
        while not self.shutdown:
            data = conn.recv(8000)
            conn.send(data)

    def close_server(self):
        self.shutdown = True


if __name__ == "__main__":
    print("Trying to run module local_servers.py directly...")
