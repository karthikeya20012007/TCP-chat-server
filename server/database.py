import psycopg2

import bcrypt

from shared.config import (
    DB_HOST,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)

connection = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = connection.cursor()


def save_message(sender, content):
    cursor.execute(
        """
        INSERT INTO messages (sender, content)
        VALUES (%s, %s)
        """,
        (sender, content)
    )

    connection.commit()
    
def get_recent_messages(limit=10):
    cursor.execute(
        """
        SELECT sender, content
        FROM messages
        ORDER BY created_at ASC
        LIMIT %s
        """,
        (limit,)
    )

    return cursor.fetchall()

def register_user(username, password):
    cursor.execute(
        """
        SELECT username
        FROM users
        WHERE username = %s
        """,
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        return False

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (%s, %s)
        """,
        (username, password_hash)
    )

    connection.commit()

    return True

def login_user(username, password):
    cursor.execute(
        """
        SELECT password_hash
        FROM users
        WHERE username = %s
        """,
        (username,)
    )

    user = cursor.fetchone()

    if not user:
        return False

    stored_password_hash = user[0]

    return bcrypt.checkpw(
        password.encode(),
        stored_password_hash.encode()
    )