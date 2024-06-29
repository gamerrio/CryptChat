import socket
import threading
import re
import keepalive
import argparse
parser = argparse.ArgumentParser(
    prog="CryptChat",
    description="A simple chat program that uses AES encryption to encrypt messages",
    epilog="Enjoy the program! :)"
)
parser.add_argument("-p", "--port", help="Port to listen on", nargs='?',type=int,action="store",const="port")
parser.add_argument("-H", "--host", help="host to listen on",nargs='?', type=str,action="store",const="host")
class Peer:
    def __init__(self,host,port):
        self.host = host
        self.port = port 
        self.peers = []
        self.announcer_host = "localhost"
        self.announcer_port = 5000
        self.connections = []
        self.connected = []
    def start_server(self):
        server_thread = threading.Thread(target=self.server)
        server_thread.start()
    
    def server(self):
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host,self.port))
            s.listen()
            print(f"Listening on {self.host}:{self.port}")
            while True:
                conn,addr = s.accept()
                print(f"Connected by {addr}")
                threading.Thread(target=self.handle_connection,args=(conn,)).start()
    def handle_connection(self,conn):
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"Received {data.decode()}")
                    if data.decode() == "/exit":
                        print("Disconnecting...")
                        conn.close()
                        break
                    conn.sendall(data)
                except Exception as err: 
                    print(f"Sorrry an error occured: {err}")
    def connect_to_peer(self,peer_host,peer_port):
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            keepalive.set(s,after_idle_sec=60, interval_sec=60, max_fails=5)
            s.connect((peer_host,peer_port))
            self.connections.append(s)
        except Exception as e:
            print(e)
    def get_peers(self):
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                s.connect((self.announcer_host,self.announcer_port))
                s.sendall((f"{self.host}:{self.port}").encode())
                data = s.recv(1024).decode()
                print("data: ",data)
                threading.Thread(args=(data,),target=self.init_connect).start()
    def init_connect(self,data):
        print("hello data: ",data)
        if ":" in data:
            for i in data.split(","):
                host_detail,name = i.split("#")
                host,port = host_detail.split(":")
                if host == self.host and port == self.port:
                    break
                if i in self.connected:
                    break
                print("Connecting to ",name)
                self.connected.append(i)
                threading.Thread(target=self.connect_to_peer,args=(host,int(port))).start()
    def send_input(self):
        while True:
                message = input("Enter Message: ")
                if message == "/exit":
                    for conn in self.connections:
                        conn.close()
                    print("Disconnecting..")
                    break
                for conn in self.connections:
                    try:    
                        conn.sendall(message.encode())
                    except (OSError, BrokenPipeError):
                        print("Connection closed")
                        self.connections.remove(conn)
if __name__ == "__main__":
    args = parser.parse_args()
    if args.port and args.host :
        peer = Peer(args.host, args.port)
    else:
        sip = str(input("Server IP&Port: ")).split(':')
        peer = Peer(sip[0], int(sip[1]))
    peer.start_server()
    cip = ["localhost","5000"]
    threading.Thread(target=peer.get_peers).start()
    threading.Thread(target=peer.connect_to_peer, args=(cip[0], int(cip[1]))).start()
    threading.Thread(target=peer.send_input).start()
