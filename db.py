import sqlite3
import hashlib

DB = "userdata.db"
DB2 = "chatdata.db"

def init_db() -> None:
    """
    Initialize the database for user accounts if it doesn't exist.

    Table structure:
        - id: Auto increment primary key integer
        - username: Unique username for each user VARCHAR(255)
        - password: Encoded hashed password VARCHAR(255)

    Returns: None

    Raises: sqlite3.Error: If there is an error creating the table.
    """
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def init_chat_db() -> None:
    """
    Initialize the database for chatlogs if it doesn't exist.

    Table structure:
        - id: Auto increment primary key integer
        - username: Recorded username of the message sender VARCHAR(255)
        - message: Text of the message TEXT
        - timestamp: Auto timestamp of when the message was sent DATETIME CURRENT_TIMESTAMP

    Returns: None

    Raises: sqlite3.Error: If there is an error creating the table.
    """
    try:
        conn = sqlite3.connect(DB2)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def hash_pw(password):
    """
    Hash the password using SHA-256.

    Args:
        - password (str): The plain text password.

    Returns: str: The hashed password.

    Encodes the pasword to bytes first before hashing and returns the hexadecimal digest.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def create_account(username, password) -> bool:
    """
    Create a new user account and store it in the database.

    Args:
        - username (str): The entered username.
        - password (str): The entered password.

    Returns: bool: True if account creation is successful, False if username is taken or error occurs.

    Raises: sqlite3.Error: If there is an error during database operations.

    Protected against SQL injection by using parameterized queries.
    """
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, hash_pw(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def check_login(username, password) -> bool:
    """
    Check if the provided username and password match an existing account.

    Args:
        - username (str): The entered username.
        - password (str): The entered password.

    Returns: bool: True if login is successful, False otherwise.

    Raises: sqlite3.Error: If there is an error during database operations.

    Protected against SQL injection by using parameterized queries.
    """
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hash_pw(password))
        )
        row = cur.fetchone()
        return row is not None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()


def save_message(username, message) -> None:
    """
    Save a chat message history to the database.

    Args:
        - username (str): The username of the message sender.
        - message (str): The text of the message.

    Returns: None

    Raises: sqlite3.Error: If there is an error during database operations.

    Protected against SQL injection by using parameterized queries.
    """
    try:
        conn = sqlite3.connect(DB2)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages(username, message) VALUES (?, ?)",
            (username, message)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
