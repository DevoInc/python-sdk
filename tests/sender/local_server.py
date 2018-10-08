import socket
import ssl
import os
from threading import Thread
from time import sleep


def deal_with_client(con_stream):
    con_stream.setblocking(5)
    data = con_stream.recv(1024)
    with open("".join((os.path.dirname(os.path.abspath(__file__)),
              os.sep, 'test_results', os.sep, 'result.txt')), 'wb') as result:
        result.write(data)
        while data:
            if not data:
                break
            data = con_stream.recv(1024)
            result.write(data)


def ssl_server():
    ca_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                            os.sep, "local_server_files", os.sep, "ca.crt"))
    cert_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                              os.sep, "local_server_files",
                              os.sep, "server.crt"))
    key_file = "".join((os.path.dirname(os.path.abspath(__file__)),
                             os.sep, "local_server_files",
                             os.sep, "server.key"))

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH,
                                         cafile=ca_file)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    bind_socket = socket.socket()
    bind_socket.bind(('0.0.0.0', 4443))
    bind_socket.listen(5)

    new_socket, from_addr = bind_socket.accept()
    con = context.wrap_socket(new_socket, server_side=True)
    try:
        deal_with_client(con)
    except Exception as error:
        print(error)
        bind_socket.close()
        con.close()
    finally:
        bind_socket().close()
        con.close()


def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 4442))
    server.listen(5)
    con, address = server.accept()
    try:
        deal_with_client(con)
    except Exception as error:
        print(error)
        server.close()
        con.close()
    finally:
        server.close()
        con.close()


def create_ssl_server():
    server = Thread(target=ssl_server, kwargs=({}))
    server.setDaemon(True)
    server.start()
    return server


def create_tcp_server():
    server = Thread(target=tcp_server, kwargs=({}))
    server.setDaemon(True)
    server.start()
    sleep(3)
    return server
