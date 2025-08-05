import socket
import threading
import subprocess

HOST = "0.0.0.0"
PORT = 2222             
USERNAME = "admin"      
PASSWORD = "1234"       

def handle_client(client_socket, address):
    client_socket.send(b"Username: ")
    username = client_socket.recv(1024).decode().strip()

    client_socket.send(b"Password: ")
    password = client_socket.recv(1024).decode().strip()

    if username != USERNAME or password != PASSWORD:
        client_socket.send(b"Auth failed. Bye.\n")
        client_socket.close()
        return

    client_socket.send(b"Welcome to the Python SSH-like server!\n$ ")

    while True:
        cmd = client_socket.recv(1024).decode().strip()
        if cmd.lower() in ["exit", "quit"]:
            client_socket.send(b"Bye!\n")
            break
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
        client_socket.send(output + b"\n$ ")

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Python SSH-like server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"[+] Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    start_server()
