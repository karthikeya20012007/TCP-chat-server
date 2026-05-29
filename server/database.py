import psycopg2

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