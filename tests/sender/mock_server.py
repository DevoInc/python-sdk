import logging,threading,os,ssl,socket,time,socket,ssl,sys
PY3 = sys.version_info[0] > 2

if not PY3:
        import SocketServer

logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s', )
logger = logging.getLogger('DEVO_logger')
logger.setLevel(logging.DEBUG)

file_path = "".join((os.path.dirname(os.path.abspath(__file__)),os.sep))
ip_server = os.getenv('DEVO_SENDER_SERVER',"0.0.0.0")
port_server = int(os.getenv('DEVO_SENDER_PORT', 4488))
tcp_server = os.getenv('DEVO_SENDER_self.tcp_server',"0.0.0.0")
tcp_port = int(os.getenv('DEVO_SENDER_self.tcp_server', 4489))
server_cert = os.getenv('DEVO_SENDER_KEY', "".join((file_path,"local_server_files",os.sep, "server.crt")))
server_key = os.getenv('DEVO_SENDER_KEY', "".join((file_path,"local_server_files",os.sep, "server.key")))

def process_stream(stream, data):
    ''''
    Process the data.
    HERE IMPLEMENT FILTERS TO DATA
    '''
    return True

def connect_client(stream):
    '''
    Read stream
    '''
    data = stream.read()
    while data:
        process_stream(stream, data)        
        data = stream.read()

def mockup_ssl_server():
    '''
    Implement the SSL SERVER
    '''
    sslSocket = socket.socket()
    sslSocket.bind((ip_server, port_server))
    sslSocket.listen(5)    
    while True:
        conn,addr = sslSocket.accept()
        stream = ssl.wrap_socket(conn,server_side=True,certfile=server_cert,keyfile=server_key)
        try:
            connect_client(stream)
        finally:
            stream.close()

if  PY3:
        def mockup_tcp_server():
                '''
                Implement the TCP SERVER
                '''    
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((tcp_server,tcp_port))
                s.listen(5)    
                conn, addr = s.accept()    
                while True:
                        data = conn.recv(1024).decode()
else:
        class CustomTCPHandler(SocketServer.StreamRequestHandler):
                def handle(self):
                        self.data = self.rfile.readline().strip()
                        self.wfile.write(self.data.upper())

        def mockup_tcp_server():
                '''
                Implement the TCP SERVER
                '''    
                server = SocketServer.TCPServer((tcp_server, tcp_port), CustomTCPHandler)
                server.serve_forever()


thread_ssl_server = threading.Thread(target=mockup_ssl_server)
thread_tcp_server = threading.Thread(target=mockup_tcp_server)

def start_server():    
    '''
    Start two servers than listen in the ports port_server and tcp_port
    '''
    thread_ssl_server.setDaemon(True)
    thread_ssl_server.start()
    thread_tcp_server.setDaemon(True)
    thread_tcp_server.start()
    logger.debug("Running the server")
    
if __name__ == "__main__":
    start_server()