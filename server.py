import socket
import threading
import user
import json
with open("config.json") as f:
    CONFIG = json.loads(f.read())
    f.close()


def handle_client(sock):
    
    try:
        uClient = user.User(sock,threading.current_thread().ident)
    except KeyboardInterrupt as e:
        print("ERROR handle_client(sock):",e)
        sock.close()
    print("Killing Thread.")


def run_server():
    host = '127.0.0.1'
    port = CONFIG['port']

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Telnet server launched! Login using: {host}:{port}")


    try:
        while True:
            sock, addr = server_socket.accept()
            print(f"Client {sock.getsockname()[0]} connected.")


            print("Starting Thread.")
            cthread = threading.Thread(target=handle_client, args=(sock,))
            cthread.start()
    except KeyboardInterrupt:
        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()
        print("Closed Socket.")

run_server()
