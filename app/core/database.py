from .config import settings
import sqlite3


def get_db_connection():
    conn = sqlite3.connect(settings.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                photo TEXT NOT NULL 
            );
        """)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                rooms_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        
def get_messages(sender_id, receiver_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM messages
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp
        ''', (sender_id, receiver_id, receiver_id, sender_id))
        return cursor.fetchall()

def get_user(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

def create_user(username, password , photo):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, photo) VALUES (?, ?, ?, ?)',
                       (username, password, photo))
        conn.commit()
        return cursor.fetchone()

def update_user(user_id, username_new, password_new, photo_new):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET username = ?, password = ?, photo = ?
            WHERE id = ?
        ''', (username_new, password_new, photo_new, user_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_user(user_id, username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ? AND username = ?', (user_id, username))
        conn.commit()
        return cursor.rowcount > 0