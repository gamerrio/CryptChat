import socket
import threading
import re
import keepalive
class Peer:
    def __init__(self,host,port):
        self.host = host
        self.port = port 
        self.peers = []
        self.announcer_host = "localhost"
        self.announcer_port = 5000
        self.connections = []
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
                # print("Nodes: ",data,"\n")
                threading.Thread(args=(data,),target=self.init_connect).start()
    def init_connect(self,data):
        for i in data.split(","):
            host_detail,name = i.split("#")
            host,port = host_detail.split(":")
            print("Connecting to ","test")
            threading.Thread(target=self.connect_to_peer,args=(host,int(port))).start()
    def send_input(self):
        while True:
                message = input("Enter Message: ")
                # if message == "/exit":
                #     for conn in self.connections:
                #         print(conn.host,conn.port)
                #         conn.close()
                #     print("Disconnecting..")
                #     break
                for conn in self.connections:
                    print(conn)
                    try:    
                        conn.sendall(message.encode())
                    except (OSError, BrokenPipeError):
                        print("Connection closed")
                        self.connections.remove(conn)
if __name__ == "__main__":
    sip = str(input("Server IP&Port: ")).split(':')
    peer = Peer(sip[0], int(sip[1]))
    peer.start_server()
    # cip = str(input("Client IP&Port")).split(':')
    cip = ["localhost","5000"]
    # Example of connecting to another peer
    threading.Thread(target=peer.get_peers).start()
    threading.Thread(target=peer.connect_to_peer, args=(cip[0], int(cip[1]))).start()
    threading.Thread(target=peer.send_input).start()
