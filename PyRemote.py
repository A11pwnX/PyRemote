import socket
import threading
import argparse
import os
import pty
import select
import sys
import time
import termios
import tty
import secrets
import string

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(secrets.choice(chars) for _ in range(length))

# -------- SERVER --------
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

# -------- CLIENT --------
def start_client(server_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))

    while True:
        data = s.recv(4096)
        if not data:
            break
        decoded = data.decode(errors="ignore")
        sys.stdout.write(decoded)
        sys.stdout.flush()

        if "Username:" in decoded or "Password:" in decoded:
            user_input = sys.stdin.readline()
            s.send(user_input.encode())
        else:
            break

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            r, _, _ = select.select([s, sys.stdin], [], [])
            if s in r:
                data = s.recv(4096)
                if not data:
                    break
                sys.stdout.write(data.decode(errors="ignore"))
                sys.stdout.flush()
            if sys.stdin in r:
                inp = sys.stdin.read(1)
                s.send(inp.encode())
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        s.close()

# -------- MAIN --------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python SSH-like tool (Server & Client in one script)")
    parser.add_argument("--mode", choices=["server", "client"], required=True, help="Run as 'server' or 'client'")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Server listen address (default: 0.0.0.0)")
    parser.add_argument("-p", "--port", type=int, default=2222, help="Port (default: 2222)")
    parser.add_argument("-u", "--username", default="admin", help="Username for auth (server mode)")
    parser.add_argument("-w", "--password", help="Password for auth (if not provided, will be auto-generated)")
    parser.add_argument("-s", "--silent", action="store_true", help="Run server in background (daemon mode)")
    parser.add_argument("-l", "--log", help="Log file path (server mode)")
    parser.add_argument("--server-ip", help="Server IP (client mode)")

    args = parser.parse_args()

    if args.mode == "server":
        if not args.password:
            args.password = generate_password()
            print(f"[!] No password provided. Generated strong password: {args.password}")
        start_server(args.host, args.port, args.username, args.password, args.log, args.silent)
    elif args.mode == "client":
        if not args.server_ip:
            print("Error: --server-ip is required in client mode.")
            sys.exit(1)
        start_client(args.server_ip, args.port)
