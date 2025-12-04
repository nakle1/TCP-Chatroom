
import socket
import threading
import sys
from datetime import datetime
from db import (
    init_db,
    create_account,
    check_login,
    init_chat_db,
    save_message
)


HOST = "127.0.0.1"
PORT = 55555

#Dictionary top keep track of connected clients username:connection
clients = {}


def broadcast(message, sender_username=None):
    """
    Broadcast a message to all connected clients except the sender.

    Iterating over the clients dictionary to send messages to the conection objects.
    Add timestamps and username to all messages then encode to utf-8 before sending.

    Args:
        - message (str): The message to broadcast.
        - sender_username (str): The username of the sender to exclude from broadcast.

    Returns: None

    Raises: Exception: If there is an error sending the message to a client.
    Silently deals with exceptions, bypassing to avoid crashing the server.
    """
    for username, conn in clients.items():
        if username == sender_username:
            continue
        try:
            now = datetime.now().time().strftime("%H:%M:%S")
            conn.sendall((f'{now} ' + message + "\n").encode('utf-8'))
        except Exception as e:
            print(f"Error broadcasting to {username}: {e}")


def handle_client(conn, addr):
    """
    Handle client connection for authentication and message receiving.

    Manages the login/signup process and message handling for a connected client.

    Args:
        - conn (socket.socket): The socket connection object for the client.
    
    Returns: None

    Raises: Exception: If there is an error during client handling.
    Silently deals with exceptions, bypassing to avoid crashing the server.

    Flow:
    1. Prompt for login (-l) or signup (-s)
    2. Handle authentication
    3. Notify all clients of new user
    4. Enter message loop
    5. Clean up on disconnect
    """
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
        conn.sendall(b"Invalid operation!\n")
        conn.close()
        return

    clients[username] = conn
    broadcast(f"{username} has joined!")

    #Main message loop
    try:
        while True:
            msg = conn.recv(1024)

            if not msg:
                break

            msg = msg.decode().strip()
            save_message(username, msg)
            broadcast(f"{username}: {msg}", username)

    except Exception as e:
        print(f"Error handling client {username}: {e}", flush=True)

    finally:
        if username in clients:
            del clients[username]
            broadcast(f"{username} has left.")
            print(f"Disconnected from {addr}", flush=True)
        conn.close()


def main():
    """
    Main server function to initialize and run the chat server.

    Sets up the server socket, listens for incoming connections, and spawns
    a new thread to handle each connected client.

    Returns: None

    Raises: KeyboardInterrupt: To handle graceful shutdown on Ctrl + C.
    Ensures all client connections are closed and the server socket is released on shutdown.
    """
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
            print(f"New connection from {addr}", flush =True)
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    except KeyboardInterrupt:
        print("\nShutting down server!")

        for conn in clients.values():
            try:
                conn.sendall(b"Server is shutting down! Goodbye!\n")
                conn.close()
            except:
                pass
        clients.clear()
        server.close()
        print("Server has closed safely!")
        sys.exit(0)


if __name__ == "__main__":
    main()
