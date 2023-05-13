import socket
import threading
import user
import json
import time
with open("config.json") as f:
    CONFIG = json.loads(f.read())
    f.close()


# quick port bypass
from sys import argv
CONFIG["port"] = int(argv[1])






def handle_client(sock,server:socket.socket):
    #sock.send(b'\xff\xfb\x18\xff\xfb\x01')

    
    try:
        uClient = user.User(sock,threading.current_thread().ident)
    except KeyboardInterrupt as e:
        print("[ERROR] handle_client(sock):",e)
        sock.close()

    if uClient.exitreason == "ServerKillCommand":
        print("[ALARM] Admin has forcibly requested a server shutdown! @",time.ctime())
        print("[ALARM] Server killed by:",threading.current_thread().ident)

        server.shutdown(socket.SHUT_RDWR)
        server.close()
        print("[SERVER] Server shutdown. (Note: The error below is expected)")
        exit()
    else:
        print(f"[SERVER] Killing Thread. Cause: {uClient.exitreason}")
    

def run_server():
    host = '127.0.0.1'
    port = CONFIG['port']

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(15)
    print(f"Telnet server launched! Login using: {host}:{port}")


    try:
        while True:
            sock, addr = server_socket.accept()
            print(f"[SERVER] Client {sock.getsockname()[0]} connected @ {time.ctime()}.")


            
            cthread = threading.Thread(target=handle_client, args=(sock,server_socket,))
            cthread.start()
    except KeyboardInterrupt:
        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()
        print("[SERVER] Closed Socket.")

run_server()