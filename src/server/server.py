from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import json

app = FastAPI()

DB_PATH = os.getenv("DATABASE_PATH", "patternauth.sqlite3")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # enable WAL mode to fix concurrency issue
    return conn

class UserCreate(BaseModel):
    username: str
    password: str
    pattern: list[int]  # pattern is list of ints

class UserLogin(BaseModel):
    username: str
    password: str

class PatternVerifyRequest(BaseModel):
    username: str
    pattern: list[int]

class PatternUpdateRequest(BaseModel):
    username: str
    pattern: list[int]

# Create a table for users (RUN ONCE)
def create_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                pattern TEXT NOT NULL,  -- Stored as JSON string
                status BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        conn.commit()

create_table()  # Ensure the table exists on startup

@app.post("/add-user/")
def add_user(user: UserCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            pattern_json = json.dumps(user.pattern)  # Convert list to JSON string
            cursor.execute("INSERT INTO users (username, password, pattern, status) VALUES (?, ?, ?, ?)",
                           (user.username, user.password, pattern_json, True))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User added successfully"}

@app.get("/user/{username}")
def get_user(username: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password, pattern, status FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

    if user:
        return {
            "password": user["password"],  # Consider hashing passwords before storing
            "pattern": json.loads(user["pattern"]),  # Convert JSON string back to list
            "status": bool(user["status"])
        }
    
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/login/")
def login(user: UserLogin):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (user.username,))
        db_user = cursor.fetchone()

    if db_user and db_user["password"] == user.password:  # Consider hashing for security
        return {"message": "Login successful"}
    
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/verify-pattern")
def verify_pattern(request: PatternVerifyRequest):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pattern FROM users WHERE username = ?", (request.username,))
        db_user = cursor.fetchone()

    if db_user:
        stored_pattern = json.loads(db_user["pattern"])  # Convert JSON string to list
        if stored_pattern == request.pattern:
            return {"message": "Pattern verified"}

    raise HTTPException(status_code=401, detail="Incorrect pattern")

@app.post("/update-pattern/")
def update_pattern(request: PatternUpdateRequest):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET pattern = ? WHERE username = ?", (str(request.pattern), request.username))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Pattern updated successfully"}


@app.post("/add-web-user/")
def add_user(user: UserCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, status) VALUES (?, ?, ?)",
                           (user.username, user.password, False))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User added successfully"}
