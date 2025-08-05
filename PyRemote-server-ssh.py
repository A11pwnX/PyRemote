import socket
import threading
import paramiko
import subprocess
import argparse
import sys

# Argument parser
parser = argparse.ArgumentParser(description="Python SSH Server")
parser.add_argument("-p", "--port", type=int, default=22, help="Specify the listening port (default: 22)")
args = parser.parse_args()

# Generate a temporary SSH host key in memory
host_key = paramiko.RSAKey.generate(2048)

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username == "admin" and password == "password":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def handle_client(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(host_key)
    server = Server()
    try:
        transport.start_server(server=server)
        chan = transport.accept(20)
        if chan is None:
            return
        chan.send("Welcome to your Python SSH server!\n$ ")

        while True:
            command = chan.recv(1024).decode().strip()
            if command.lower() in ("exit", "quit"):
                chan.send("Goodbye!\n")
                break
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            except Exception as e:
                output = str(e).encode()
            chan.send(output + b"\n$ ")
    except Exception as e:
        print("Error:", e)
    finally:
        transport.close()

# TCP server listening on the specified port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind(("0.0.0.0", args.port))
except PermissionError:
    print(f"[!] Permission denied: You need root privileges to bind to port {args.port}")
    sys.exit(1)

server_socket.listen(100)
print(f"[*] Python SSH server listening on port {args.port}")

while True:
    client, addr = server_socket.accept()
    print(f"Incoming connection: {addr}")
    threading.Thread(target=handle_client, args=(client,)).start()
