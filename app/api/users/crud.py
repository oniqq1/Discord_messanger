from app.core.database import get_db_connection


def get_user(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

def create_user(username, password , photo):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, photo) VALUES (?, ?, ?)',
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