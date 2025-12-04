import socket
import threading
import sys
import signal

# Server connection configuration
HOST = "localhost"
PORT = 55555

# Global socket reference for signal handler access
sock = None


def listen_to_server(sock):
    """
    Continuously receive and display messages from the server.
    
    Args:
        sock (socket.socket): Connected socket to the server
    
    Returns:
        None

    Flow:
        1. Receive data from server
        2. Decode and print messages
        3. Handle disconnections and errors gracefully
    """
    while True:
        try:
            data = sock.recv(1024)
            
            if not data:
                print("\nDisconnected from server.")
                sys.exit(0)
            
            message = data.decode().rstrip()
            if message:
                print(message)
                
        except ConnectionResetError:
            print("\nConnection to server lost.")
            sys.exit(0)
        except OSError:
            print("\nSocket closed.")
            sys.exit(0)
        except Exception as e:
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
    while True:
        try:
            msg = input()
            if msg:
                sock.sendall((msg + '\n').encode())
        except (BrokenPipeError, ConnectionResetError):
            print("\nConnection to server lost.")
            sys.exit(0)
        except EOFError:
            print("\nExiting.")
            sys.exit(0)
        except OSError:
            print("\nSocket closed.")
            sys.exit(0)
        except Exception as e:
            print(f"\nFailed to send message: {e}")
            sys.exit(0)


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
    global sock

    if sock:
        try:
            sock.close()
        except Exception:
            pass
    
    print("\nDisconnected.")
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
    
    signal.signal(signal.SIGINT, signal_handler)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((HOST, PORT))
        print("Connected to server!\n")
    except ConnectionRefusedError:
        print(f"Could not connect to server at {HOST}:{PORT}")
        sys.exit(1)
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)
    
    listener_thread = threading.Thread(target=listen_to_server, args=(sock,), daemon=True)
    listener_thread.start()
    
    try:
        send_to_server(sock)
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()