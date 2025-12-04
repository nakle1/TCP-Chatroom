# import socket
# import threading
# import sys

# HOST = "localhost"
# PORT = 55555


# def listen_to_server(sock):
#     while True:
#         try:
#             data = sock.recv(1024)
#             if not data:
#                 print("Disconnected from server.")
#                 sys.exit(0)
#             print(data.decode().rstrip())
#         except:
#             print("Connection error.")
#             sock.exit(0)
#             sys.exit(0)


# def send_to_server(sock):
#     while True:
#         try:
#             msg = input()
#             if msg:
#                 sock.sendall(msg.encode())
#         except:
#             print("Failed to send message.")
#             sys.exit(0)


# def main():
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect((HOST, PORT))

#     threading.Thread(target=listen_to_server, args=(sock,)).start()
#     send_to_server(sock)


# if __name__ == "__main__":
#     main()

"""
Chat client implementation using socket programming.

Connects to server, handles authentication, and enables real-time messaging
with graceful shutdown on Ctrl+C.
"""

import socket
import threading
import sys
import signal

# Server connection configuration
HOST = "localhost"
PORT = 55555

# Global socket reference for signal handler access
sock = None
# Flag to indicate if we should exit
should_exit = False


def listen_to_server(sock):
    """
    Continuously receive and display messages from the server.
    
    Runs in a separate thread to allow simultaneous receiving and sending.
    Exits gracefully on disconnect or connection errors.
    
    Args:
        sock (socket.socket): Connected socket to the server
    
    Returns:
        None
    """
    global should_exit
    
    while not should_exit:
        try:
            data = sock.recv(1024)
            
            # Empty data means server closed connection
            if not data:
                print("\nDisconnected from server.")
                should_exit = True
                # Force exit to unblock the input() in send_to_server
                sys.exit(0)
            
            # Display received message
            message = data.decode().rstrip()
            print(message)
            
            # Check if server is kicking us out (error messages)
            if any(keyword in message.lower() for keyword in [
                "username already taken",
                "invalid login",
                "invalid operation",
                "already logged in"
            ]):
                # Give user time to read the message
                threading.Timer(1.0, lambda: sys.exit(0)).start()
                
        except ConnectionResetError:
            print("\nConnection to server lost.")
            should_exit = True
            sys.exit(0)
        except Exception as e:
            if not should_exit:
                print(f"\nConnection error: {e}")
            sys.exit(0)


def send_to_server(sock):
    """
    Continuously read user input and send to server.
    
    Runs in the main thread, blocking on stdin to read user messages.
    Each line of input is sent to the server immediately.
    
    Args:
        sock (socket.socket): Connected socket to the server
    
    Returns:
        None
    """
    global should_exit
    
    while not should_exit:
        try:
            # Read line from user input
            msg = input()
            
            if msg and not should_exit:
                sock.sendall((msg + '\n').encode())
                
        except EOFError:
            # Ctrl+D pressed or input closed
            should_exit = True
            break
        except (BrokenPipeError, ConnectionResetError):
            if not should_exit:
                print("\nConnection to server lost.")
            should_exit = True
            break
        except Exception as e:
            if not should_exit:
                print(f"\nFailed to send message: {e}")
            should_exit = True
            break


def signal_handler(sig, frame):
    """
    Handle Ctrl+C (SIGINT) for graceful client shutdown.
    
    Closes the socket connection and exits cleanly when user presses Ctrl+C.
    
    Args:
        sig (int): Signal number (SIGINT)
        frame: Current stack frame (unused)
    
    Returns:
        None
    """
    global should_exit
    should_exit = True
    
    print("\n\nDisconnecting from server...")
    
    if sock:
        try:
            sock.close()
        except Exception:
            pass
    
    print("Disconnected.")
    sys.exit(0)


def main():
    """
    Main client entry point.
    
    Establishes connection to server, registers signal handler for Ctrl+C,
    and starts listener and sender threads.
    
    Returns:
        None
    
    Flow:
        1. Register Ctrl+C handler
        2. Connect to server
        3. Start listener thread for receiving messages
        4. Run sender loop in main thread for user input
    """
    global sock
    
    # Register Ctrl+C (SIGINT) handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Attempt to connect to server
    try:
        print(f"Connecting to {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        print("Connected to server!\n")
    except ConnectionRefusedError:
        print(f"Could not connect to server at {HOST}:{PORT}")
        print("Is the server running?")
        sys.exit(1)
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)
    
    # Start listener thread (daemon=True means thread exits when main exits)
    listener_thread = threading.Thread(
        target=listen_to_server,
        args=(sock,),
        daemon=True
    )
    listener_thread.start()
    
    # Run sender in main thread (blocks on input)
    send_to_server(sock)
    
    # Clean up when send_to_server exits
    if sock:
        sock.close()


if __name__ == "__main__":
    main()
