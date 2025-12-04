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
                sys.exit(0)
            
            message = data.decode().rstrip()
            print(message)
            
            if any(keyword in message for keyword in [
                "Username already taken",
                "Invalid login",
                "Invalid operation"
            ]):
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
            msg = input()
            
            if msg and not should_exit:
                sock.sendall((msg + '\n').encode())

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
    
    signal.signal(signal.SIGINT, signal_handler)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
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
    
    listener_thread = threading.Thread(target=listen_to_server, args=(sock,), daemon=True)
    listener_thread.start()
    
    send_to_server(sock)
    
    if sock:
        sock.close()


if __name__ == "__main__":
    main()
