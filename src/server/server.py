from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

DB_PATH = os.getenv("DATABASE_PATH", "patternauth.sqlite3")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
    return conn

class UserCreate(BaseModel):
    username: str
    password: str
    pattern: list[int]

class UserLogin(BaseModel):
    username: str
    password: str

class PatternVerifyRequest(BaseModel):
    username: str
    pattern: list[int]


# Create a table for users
@app.post("/user/")
def add_user(user: UserCreate):
    with get_db_connection() as conn:  # Use context manager for automatic connection closing
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, pattern, status) VALUES (?, ?, ?, ?)",
                           (user.username, user.password, user.pattern, True))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User added successfully"}

# Get user details by username
@app.get("/user/{username}")
def get_user(username: str):
    with get_db_connection() as conn:  # Use context manager for automatic connection closing
        cursor = conn.cursor()
        cursor.execute("SELECT password, pattern, status FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

    if user:
        return {
            "password": user["password"],  # Consider hashing passwords before storing
            "pattern": user["pattern"],
            "status": bool(user["status"])  # Convert to a proper boolean
        }
    
    raise HTTPException(status_code=404, detail="User not found")

# Login with username and password
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT pattern FROM users WHERE username = ?", (request.username,))
    db_user = cursor.fetchone()
    conn.close()
    
    if db_user and db_user["pattern"] == request.pattern:
        return {"message": "Pattern verified"}
    
    raise HTTPException(status_code=401, detail="Incorrect pattern")