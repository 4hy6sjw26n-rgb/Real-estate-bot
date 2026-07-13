import sqlite3
from datetime import datetime

DB_NAME = "requests.db"


def create_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            type TEXT,
            name TEXT,
            phone TEXT,
            description TEXT,
            property TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def save_to_database(data):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO requests (
            created_at,
            type,
            name,
            phone,
            description,
            property
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("type"),
            data.get("name"),
            data.get("phone"),
            data.get("text"),
            data.get("property"),
        ),
    )

    connection.commit()
    connection.close()