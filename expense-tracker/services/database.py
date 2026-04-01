import sqlite3
import os

DB_PATH = "data/expenses.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Creates the expenses table if it does not exist."""
    # Make sure the data folder exists
    os.makedirs("data", exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            currency TEXT,
            converted_amount REAL,
            split_type TEXT,
            participants TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")