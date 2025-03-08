import sqlite3
import os

DB_PATH = os.getenv("DATABASE_PATH", "patternauth.sqlite3")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create the 'users' table if it does not exist, and add 'last_pattern_update' column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        pattern TEXT NOT NULL,
        status BOOLEAN NOT NULL,
        last_pattern_update TEXT
    )
''')

conn.commit()
conn.close()

print("Database initialized successfully!")