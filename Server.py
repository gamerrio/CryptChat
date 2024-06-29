import socket
import threading
import keepalive
class Server:
    def __init__(self):
        self.clients =[]
        self.usr_list = ''
    def handle_client(self,client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
                if ":" in str(data.decode()):
                    self.on_join(data)
                    client_socket.sendall(self.usr_list.encode())
            except ConnectionResetError:
                break
        client_socket.close()


    def on_join(self,data):
            for i in self.clients:
                host, port = data.decode().split(":")
                if self.usr_list == '':
                    self.usr_list = self.usr_list + f"{host}:{port}#name"
                else:
                    self.usr_list = self.usr_list + f",{host}:{port}#name"
                i.sendall(self.usr_list.encode())
            

    def start_server(self,host='0.0.0.0', port=5000):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        print(f"Server listening on {host}:{port}")

        while True:
            client_socket, addr = server.accept()
            keepalive.set(client_socket,after_idle_sec=60, interval_sec=60, max_fails=5)
            self.clients.append(client_socket)
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    Server().start_server()