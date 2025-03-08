from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import json
import bcrypt
from cryptography.fernet import Fernet

# Load encryption key from environment variable
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY is not set!")

cipher = Fernet(ENCRYPTION_KEY.encode())

app = FastAPI()
DB_PATH = os.getenv("DATABASE_PATH", "patternauth.sqlite3")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode
    return conn

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PatternVerifyRequest(BaseModel):
    username: str
    pattern: list[int]

class PatternUpdateRequest(BaseModel):
    username: str
    pattern: list[int]


class WebUserCreate(BaseModel):
    username: str
    password: str

# Create a table for users (RUN ONCE)
# Hash password
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# Encrypt pattern
def encrypt_pattern(pattern: list[int]) -> str:
    pattern_json = json.dumps(pattern)
    encrypted = cipher.encrypt(pattern_json.encode())
    return encrypted.decode()

# Decrypt pattern
def decrypt_pattern(encrypted_pattern: str) -> list[int]:
    decrypted = cipher.decrypt(encrypted_pattern.encode()).decode()
    return json.loads(decrypted)

# Create users table
def create_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                pattern TEXT NOT NULL,
                status BOOLEAN NOT NULL DEFAULT 1
            )
        """)
        conn.commit()

create_table()

@app.post("/add-user/")
def add_user(user: UserCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(user.password)
            cursor.execute("INSERT INTO users (username, password, status) VALUES (?, ?, ?)",
                           (user.username, hashed_password, True))
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
            "password": user["password"],
            "pattern": decrypt_pattern(user["pattern"]),
            "status": bool(user["status"])
        }
    
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/login/")
def login(user: UserLogin):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (user.username,))
        db_user = cursor.fetchone()

    if db_user and verify_password(user.password, db_user["password"]):
        return {"message": "Login successful"}
    
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/verify-pattern")
def verify_pattern(request: PatternVerifyRequest):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pattern FROM users WHERE username = ?", (request.username,))
        db_user = cursor.fetchone()

    if db_user:
        stored_pattern = decrypt_pattern(db_user["pattern"])
        if stored_pattern == request.pattern:
            return {"message": "Pattern verified"}

    raise HTTPException(status_code=401, detail="Incorrect pattern")

@app.post("/update-pattern/")
def update_pattern(request: PatternUpdateRequest):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        encrypted_pattern = encrypt_pattern(request.pattern)
        cursor.execute("UPDATE users SET pattern = ? WHERE username = ?", (encrypted_pattern, request.username))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Pattern updated successfully"}


    
@app.post("/add-web-user/")
def add_user(user: WebUserCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                           (user.username, user.password))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User added successfully"}

