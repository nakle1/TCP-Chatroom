
import socket
import threading
import sys
from db import init_db, create_account, check_login, init_chat_db, save_message
from datetime import datetime

HOST = "127.0.0.1"
PORT = 55555

clients = {} #username: conn


def broadcast(message, sender_username=None):
    for username, conn in clients.items():
        if username == sender_username:
            continue
        try:

            now = datetime.now().time().strftime("%H:%M:%S")
            conn.sendall((f'{now} ' + message + "\n").encode())
        except:
            pass


def handle_client(conn, addr):
    conn.sendall(b"Welcome to the chatroom!\nDo you want to login (-l) or signup (-s)? ")

    choice = conn.recv(1024).decode().strip().lower()

    if choice == "-s":
        conn.sendall(b"Choose a username: ")
        username = conn.recv(1024).decode().strip()

        conn.sendall(b"Choose a password: ")
        password = conn.recv(1024).decode().strip()

        if create_account(username, password):
            conn.sendall(b"Account created!\n")
        else:
            conn.sendall(b"Username already taken.\n")
            conn.close()
            return       
    elif choice == "-l":
        conn.sendall(b"Username: ")
        username = conn.recv(1024).decode().strip()

        conn.sendall(b"Password: ")
        password = conn.recv(1024).decode().strip()

        if not check_login(username, password):
            conn.sendall(b"Invalid login.\n")
            conn.close()
            return
    else:
        conn.sendall(b"Invalid operation")
        conn.close()
        return

    clients[username] = conn
    broadcast(f"{username} has joined!")

    try:
        while True:
            msg = conn.recv(1024)
            if not msg:
                break

            msg = msg.decode().strip()
            save_message(username, msg)
            broadcast(f"{username}: {msg}", username)

    except:
        pass

    finally:
        del clients[username]
        broadcast(f"{username} has left.")
        conn.close()


def main():
    init_db()
    init_chat_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server running on port", PORT)
    print("Press Ctrl + C to shutdown server")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    except KeyboardInterrupt:
        print("\nShutting down server!")

        for conn in clients.values():
            try:
                conn.sendall(b"Server is shutting down!")
                conn.close()
            except:
                pass
        clients.clear()
        server.close()
        print("Server has closed safely!")
        sys.exit(0)


if __name__ == "__main__":
    main()
