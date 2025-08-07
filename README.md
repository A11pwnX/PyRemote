# PyRemote

## Description

PyRemote is a lightweight Python-based remote shell tool for quick terminal access over TCP.  
It is designed for **testing, debugging, and development in controlled environments**, especially on systems where installing OpenSSH is not practical.

Unlike a reverse shell (where the client connects back and keeps its port closed), **PyRemote requires the server to listen on an open port** that clients connect to, similar to SSH.  

However, PyRemote is **not encrypted** and should only be used in safe, local networks or isolated environments.

---

## Important Notes

- PyRemote is **not a secure replacement for SSH**.
- It does **not encrypt traffic**. All information, including passwords, is sent in plaintext.
- It is designed for **trusted local networks or isolated lab environments only**.
- **Do not expose PyRemote to the internet** or public-facing networks under any circumstances.
- PyRemote is **not a reverse shell**: the server must have an open port, and clients connect to it.
- Intended only for **testing, debugging, or educational use**.

---

## Features

- Pure Python 3, no external dependencies.
- Interactive TTY session (supports arrow keys, Ctrl+C, etc.).
- Username/password authentication (auto-generated strong password if not provided).
- Optional logging with configurable file path.
- Background (daemon) mode for the server.
- Three scripts provided:
  - `PyRemote-server.py` – Standalone server.
  - `PyRemote-client.py` – Standalone client.
  - `PyRemote.py` – Combined server and client in one file.
- Works on any system with Python 3, ideal for exotic or minimal OS environments.

---

## Installation

Clone the repository:
```bash
git clone https://github.com/A11pwnX/PyRemote.git
cd PyRemote
```


---

## Usage

### Server Help

```bash
python3 PyRemote-server.py -h
```

**Output:**
```
usage: PyRemote-server.py [-h] [-H HOST] [-p PORT] [-u USERNAME] [-w PASSWORD] [-s] [-l LOG]

options:
  -h, --help            Show this help message and exit
  -H HOST, --host HOST  Server listen address (default: 0.0.0.0)
  -p PORT, --port PORT  Port to listen on (default: 2222)
  -u USERNAME, --username USERNAME
                        Username for authentication (default: admin)
  -w PASSWORD, --password PASSWORD
                        Password for authentication (if not provided, a random one is generated)
  -s, --silent          Run the server in background (daemon mode)
  -l LOG, --log LOG     Log file path
```

### Client Help

```bash
python3 PyRemote-client.py -h
```

**Output:**
```
usage: PyRemote-client.py [-h] -s SERVER [-p PORT]

options:
  -h, --help            Show this help message and exit
  -s SERVER, --server SERVER
                        Server IP or hostname to connect to
  -p PORT, --port PORT  Server port (default: 2222)
```

---

## Examples

**Run the server in the foreground:**
```bash
python3 PyRemote-server.py -H 0.0.0.0 -p 2222 -u admin -w mypassword
```

**Run the server in background with logging:**
```bash
python3 PyRemote-server.py -H 0.0.0.0 -p 2222 -u admin -s -l /tmp/pyremote.log
```

**If no password is provided:**
```bash
python3 PyRemote-server.py -H 0.0.0.0 -p 2222 -u admin
```
This will generate a random strong password and display it at launch.

**Connect from a client:**
```bash
python3 PyRemote-client.py -s 192.168.1.10 -p 2222
```

**Using the combined script:**

*Start the server:*
```bash
python3 PyRemote.py --mode server -H 0.0.0.0 -p 2222 -u admin
```

*Connect as a client:*
```bash
python3 PyRemote.py --mode client --server-ip 192.168.1.10 -p 2222
```

---

## Repository Structure

```
PyRemote/
│
├── PyRemote-server.py    # Serveur autonome
├── PyRemote-client.py    # Client autonome
├── PyRemote.py           # Serveur & client combinés
└── Misc/
    ├── PyRemote-client-notty.py
    ├── PyRemote-server-notty.py
    └── PyRemote-server-ssh.py
```
---

## Disclaimer

PyRemote is for local, trusted networks or isolated environments only.  
It is intended solely for testing, debugging, and educational purposes.  
The authors disclaim any responsibility for misuse or insecure deployments.
