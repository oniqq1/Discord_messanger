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
                roomname INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roomname TEXT NOT NULL UNIQUE,
                members TEXT NOT NULL
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



def add_message(sender_id, roomname, content):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (sender_id, roomname, content)
            VALUES (?, ?, ?)
        ''', (sender_id, roomname, content))
        conn.commit()
        conn.close()


    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT members FROM rooms WHERE roomname = ?''', (roomname,))
        members_new = cursor.fetchone()
        conn.close()


    members = members_new[0]

    members += f', {sender_id} '

    with get_db_connection()  as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO rooms (roomname , members) VALUES (?, ?)', (roomname, members))
        conn.commit()
        conn.close()

    return members


def add_room(roomname, user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rooms WHERE roomname=?', (roomname,))
        room = cursor.fetchone()
        conn.commit()

    if not room:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO rooms (roomname, members) VALUES (?, ?)', (roomname, f'{user_id}'))
            conn.commit()
    else:

        return 'Room already exists'


def add_member_to_room(roomname, user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT members FROM rooms WHERE roomname = ?', (roomname,))
        members_new = list(cursor.fetchone())

    if members_new:
        members = members_new[0]

        if str(user_id) in members.split(','):
            return 'User already in room'

        members_new[0] += f',{user_id}'

        with get_db_connection()  as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE rooms SET members = ? WHERE roomname = ?', (members_new[0], roomname))
            conn.commit()


        return members_new[0]
    else:
        return 'Room does not exist'