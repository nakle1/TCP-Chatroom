import sqlite3
import hashlib

DB = "userdata.db"
DB2 = "chatdata.db"

def init_db():
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
    conn.close()


def init_chat_db():
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
    conn.close()


def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_account(username, password):
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(username, password) VALUES (?, ?)",
            (username, hash_pw(password))
        )
        conn.commit()
        conn.close()
        return True
    except:
        return False


def check_login(username, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    )
    row = cur.fetchone()
    conn.close()
    return row is not None

def save_message(username, message):
    conn = sqlite3.connect(DB2)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages(username, message) VALUES (?, ?)",
        (username, message)
    )
    conn.commit()
    conn.close()
