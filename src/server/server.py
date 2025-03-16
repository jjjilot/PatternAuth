from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import json
import bcrypt
from cryptography.fernet import Fernet
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

# Load encryption key from environment variable
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY is not set!")

cipher = Fernet(ENCRYPTION_KEY.encode())

app = FastAPI()

#To get around the issue of an Option call
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins instead of "*"
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # This allows all headers
)
# More env variables
DB_PATH = os.getenv("DATABASE_PATH", "patternauth.sqlite3")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode (bug fix)
    return conn

# query classes
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

class PatternUpdateRequest(BaseModel):
    username: str
    pattern: list[int]


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

# Function to check if 7 days have passed
def has_expired(last_update: str) -> bool:
    if not last_update:
        return True  # If no date exists, force reset
    last_update_dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
    return datetime.now() - last_update_dt > timedelta(days=7) 

@app.post("/add-user/")
def add_user(user: UserCreate):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(user.password)
            encrypted_pattern = encrypt_pattern([0,0,0,0,0,0,0,0,0])
            last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO users (username, password, pattern, status, last_pattern_update) VALUES (?, ?, ?, ?, ?)",
                           (user.username, hashed_password, encrypted_pattern, False, last_update))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User added successfully"}

@app.get("/user/{username}")
def get_user(username: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password, pattern, status, last_pattern_update FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            last_update = user["last_pattern_update"]
            if has_expired(last_update):
                # Reset pattern if 7 days have passed
                reset_pattern = encrypt_pattern([0,0,0,0,0,0,0,0,0])
                new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE users SET pattern = ?, last_pattern_update = ? WHERE username = ?", 
                               (reset_pattern, new_timestamp, username))
                conn.commit()
                return {
                    "password": user["password"],
                    "pattern": [0,0,0,0,0,0,0,0,0],  # Return reset pattern
                    "status": bool(user["status"])
                }
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
        cursor.execute("SELECT password, last_pattern_update FROM users WHERE username = ?", (user.username,))
        db_user = cursor.fetchone()

    if db_user and verify_password(user.password, db_user["password"]):
        # Check if 7 days have passed since last pattern update
        last_update = db_user["last_pattern_update"]
        if has_expired(last_update):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                reset_pattern = encrypt_pattern([0,0,0,0,0,0,0,0,0])
                new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE users SET pattern = ?, last_pattern_update = ? WHERE username = ?", 
                               (reset_pattern, new_timestamp, user.username))
                conn.commit()
            return {"message": "Login successful, but pattern reset due to expiration"}

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
        # Retrieve the current encrypted pattern for the user
        cursor.execute("SELECT pattern FROM users WHERE username = ?", (request.username,))
        db_user = cursor.fetchone()

        if db_user:
            # Decrypt the current pattern
            current_pattern = decrypt_pattern(db_user["pattern"])

            # Check if the new pattern is the same as the old one
            if current_pattern == request.pattern:
                raise HTTPException(status_code=400, detail="New pattern cannot be the same as the old pattern")

            # If patterns are different, encrypt the new pattern and update it
            encrypted_pattern = encrypt_pattern(request.pattern)
            new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE users SET pattern = ?, last_pattern_update = ? WHERE username = ?", 
                           (encrypted_pattern, new_timestamp, request.username))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Pattern updated successfully"}

@app.get("/last-update/{username}")
def get_last_update(username: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT last_pattern_update FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

    if user and user["last_pattern_update"]:
        return {"username": username, "last_pattern_update": user["last_pattern_update"]}
    
    raise HTTPException(status_code=404, detail="User not found")
