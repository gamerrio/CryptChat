import socket
import threading
usr_list = 'localhost:5002#Name'

def handle_client(client_socket):
    global usr_list
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode()}")
            if ":" in str(data.decode()):
                host, port = data.decode().split(":")
                # usr_list = usr_list + f",{host}:{port}#name"
                client_socket.sendall(usr_list.encode("utf-8"))
            client_socket.sendall(data)
        except ConnectionResetError:
            break
    client_socket.close()


def on_join(sock):
    sock.sendall(usr_list.encode())
    usr_list.append()


def start_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()