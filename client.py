import socket
import threading
import sys

HOST = "localhost"
PORT = 55555


def listen_to_server(sock):
    """Continuously read and print messages from server."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Disconnected from server.")
                sys.exit(0)
            print(data.decode().rstrip())
        except:
            print("Connection error.")
            sys.exit(0)


def send_to_server(sock):
    """Continuously send user input to server."""
    while True:
        try:
            msg = sys.stdin.readline()
            if msg:
                sock.sendall(msg.encode())
        except:
            print("Failed to send message.")
            sys.exit(0)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    threading.Thread(target=listen_to_server, args=(sock,)).start()
    send_to_server(sock)


if __name__ == "__main__":
    main()
