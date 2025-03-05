from fastapi import FastAPI, HTTPException
import sqlite3
import os

app = FastAPI()

# Ensure SQLite database is in a persistent storage path
DB_PATH = os.getenv("DATABASE_PATH", "patternauth.sqlite3")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/user/{username}")
def get_user(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, pattern, status FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "username": user["username"],
            "password": user["password"],  # Hash passwords before storing
            "pattern": user["pattern"],
            "status": bool(user["status"])
        }
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/user/")
def add_user(username: str, password: str, pattern: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, pattern, status) VALUES (?, ?, ?, ?)",
                       (username, password, pattern, True))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()
    return {"message": "User added successfully"}

# Run locally with: uvicorn app:app --host 0.0.0.0 --port 8000