import socket
import argparse
import sys
import termios
import tty
import select

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini SSH-like Client")
    parser.add_argument("-s", "--server", required=True, help="Server IP or hostname to connect to")
    parser.add_argument("-p", "--port", type=int, default=2222, help="Server port (default: 2222)")
    args = parser.parse_args()

    start_client(args.server, args.port)
