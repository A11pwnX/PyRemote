import socket

HOST = "192.168.1.37"   
PORT = 2222

def client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    while True:
        data = s.recv(4096)
        if not data:
            break
        print(data.decode(), end="")
        user_input = input()
        s.send((user_input + "\n").encode())
        if user_input.lower() in ["exit", "quit"]:
            break

    s.close()

if __name__ == "__main__":
    client()
