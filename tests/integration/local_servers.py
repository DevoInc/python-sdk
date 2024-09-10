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
        if num_tries == 0:
            raise Exception("Connection to address %s at port %d could not be established" % (address, port))


class EchoServer:

    def __init__(self, ip="127.0.0.1", port=4488, certfile=None, keyfile=None, ssl=True):
        self.ip = ip
        self.port = port
        self.cert = certfile
        self.key = keyfile
        self.shutdown = False
        self.ssl = ssl
        self.file_path = "".join((os.path.dirname(os.path.abspath(__file__)), os.sep))
        self.server_process = multiprocessing.Process(target=self.server, name="sslserver" if ssl else "tcpserver")
        self.server_process.start()

    def server(self):
        asyncio.run(self.run_server())

    async def run_server(self):

        async def handle_connection(reader, writer):
            addr = writer.get_extra_info("peername")
            try:
                while not self.shutdown:
                    data = await reader.read(500)
                    assert len(data) > 0, repr(data)
                    print("Server received {!r} from {}".format(data, addr))
                    writer.write(data)
                    await writer.drain()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                writer.close()
                await writer.wait_closed()

        # Create SSL context
        sc = None
        if self.ssl:
            sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            sc.load_cert_chain(self.cert, self.key)

        # Run server
        server = await asyncio.start_server(handle_connection, self.ip, self.port, ssl=sc)

        print("Serving SSL on {}".format(server.sockets[0].getsockname()))

        async with server:
            # Server runs forever (until closed)
            await server.serve_forever()

    def close_server(self):
        self.shutdown = True
        self.server_process.terminate()
        self.server_process.join()


if __name__ == "__main__":
    print("Trying to run module local_servers.py directly...")
