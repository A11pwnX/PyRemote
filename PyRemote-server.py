import socket
import threading
import argparse
import os
import pty
import select
import sys
import time
import secrets
import string

def generate_password(length=16):
    """Generate a strong random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(secrets.choice(chars) for _ in range(length))

def log_event(logfile, message):
    if logfile:
        with open(logfile, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def handle_client(client_socket, username, password, logfile):
    client_socket.send(b"Username: ")
    user = client_socket.recv(1024).decode().strip()

    client_socket.send(b"Password: ")
    passwd = client_socket.recv(1024).decode().strip()

    if user != username or passwd != password:
        client_socket.send(b"Auth failed. Bye.\n")
        log_event(logfile, f"Auth failed for {user} from {client_socket.getpeername()[0]}")
        client_socket.close()
        return

    client_socket.send(b"Welcome! Starting TTY session...\r\n")
    log_event(logfile, f"Auth success for {user} from {client_socket.getpeername()[0]}")

    pid, fd = pty.fork()
    if pid == 0:
        os.execlp("bash", "bash")
    else:
        while True:
            r, _, _ = select.select([client_socket, fd], [], [])
            if client_socket in r:
                data = client_socket.recv(1024)
                if not data:
                    break
                os.write(fd, data)
            if fd in r:
                try:
                    data = os.read(fd, 1024)
                except OSError:
                    break
                if not data:
                    break
                client_socket.send(data)

    client_socket.close()

def start_server(host, port, username, password, logfile, silent):
    if silent:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        os.setsid()
        pid = os.fork()
        if pid > 0:
            sys.exit(0)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    log_event(logfile, f"Server started on {host}:{port}")
    print(f"[*] Listening on {host}:{port} (user: {username} | password: {password})")

    while True:
        client_socket, addr = server.accept()
        log_event(logfile, f"Connection from {addr[0]}")
        print(f"[+] Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, username, password, logfile)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini SSH-like Server")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Host to listen on (default: 0.0.0.0)")
    parser.add_argument("-p", "--port", type=int, default=2222, help="Port (default: 2222)")
    parser.add_argument("-u", "--username", default="admin", help="Authentication username (default: admin)")
    parser.add_argument("-w", "--password", help="Authentication password (if not set, will be auto-generated)")
    parser.add_argument("-s", "--silent", action="store_true", help="Run in background (daemon mode)")
    parser.add_argument("-l", "--log", help="Log file path (e.g., /tmp/sshlog.txt)")

    args = parser.parse_args()

    if not args.password:
        args.password = generate_password()
        print(f"[!] No password provided. Generated strong password: {args.password}")

    start_server(args.host, args.port, args.username, args.password, args.log, args.silent)
