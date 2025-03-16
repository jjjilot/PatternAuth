from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import json
import bcrypt
from cryptography.fernet import Fernet
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

# ------------------------------------------------------------------------
# CONFIG & SETUP
# ------------------------------------------------------------------------
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY is not set!")

cipher = Fernet(ENCRYPTION_KEY.encode())
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv("DATABASE_PATH", "patternauth.sqlite3")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode
    return conn

# ------------------------------------------------------------------------
# Pydantic Models
# ------------------------------------------------------------------------
class UserCreate(BaseModel):
    username: str
    password: str
    # For brand-new users, we ignore 'pattern' on the phone side or pass an empty list.
    pattern: list[int] = []

class UserLogin(BaseModel):
    username: str
    password: str

class PatternVerifyRequest(BaseModel):
    username: str
    pattern: list[int]

class PatternUpdateRequest(BaseModel):
    username: str
    pattern: list[int]

# ------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def encrypt_pattern(pattern: list[int]) -> str:
    pattern_json = json.dumps(pattern)
    encrypted = cipher.encrypt(pattern_json.encode())
    return encrypted.decode()

def decrypt_pattern(encrypted_pattern: str) -> list[int]:
    decrypted = cipher.decrypt(encrypted_pattern.encode()).decode()
    return json.loads(decrypted)

def has_expired(last_update: str) -> bool:
    if not last_update:
        return False  # For brand-new user, treat them as "not expired" yet
    last_update_dt = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
    return (datetime.now() - last_update_dt) > timedelta(days=7)

# ------------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------------

# ----------------------
# 1) CREATE NEW USER
# ----------------------
@app.post("/add-user/")
def add_user(user: UserCreate):
    """
    Creates a brand-new user with:
      - hashed password
      - default pattern of all zeros (9-length)
      - status = False initially
      - last_pattern_update = now (so they're not forced expired)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(user.password)
            default_pattern = encrypt_pattern([0,0,0,0,0,0,0,0,0])  # 9 zeros
            last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                INSERT INTO users (username, password, pattern, status, last_pattern_update)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user.username, hashed_password, default_pattern, False, last_update),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Username already exists")

    return {"message": "User added successfully"}

# ----------------------
# 2) GET USER DETAILS
# ----------------------
@app.get("/user/{username}")
def get_user(username: str):
    """
    Returns:
      - password (hashed)
      - decrypted pattern
      - status (bool)
    
    If 7 days have passed, sets user.status = False (but does not overwrite pattern).
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT password, pattern, status, last_pattern_update 
            FROM users WHERE username = ?
            """,
            (username,),
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        last_update = user["last_pattern_update"]

        if has_expired(last_update):
            # Mark as expired in DB by setting status to False
            cursor.execute(
                """
                UPDATE users
                SET status = 0
                WHERE username = ?
                """,
                (username,),
            )
            conn.commit()
            return {
                "password": user["password"],
                "pattern": decrypt_pattern(user["pattern"]),
                "status": False,
            }
        else:
            return {
                "password": user["password"],
                "pattern": decrypt_pattern(user["pattern"]),
                "status": bool(user["status"]),
            }

# ----------------------
# 3) LOGIN
# ----------------------
@app.post("/login/")
def login(user: UserLogin):
    """
    Validates username/password. If more than 7 days since last pattern update, 
    sets status = False. Otherwise, user remains with same status.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT password, last_pattern_update
            FROM users
            WHERE username = ?
            """,
            (user.username,),
        )
        db_user = cursor.fetchone()

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Now check expiration
    last_update = db_user["last_pattern_update"]
    if has_expired(last_update):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET status = 0
                WHERE username = ?
                """,
                (user.username,),
            )
            conn.commit()
        return {"message": "Login successful, but pattern expired; user status set to false."}

    return {"message": "Login successful"}

# ----------------------
# 4) VERIFY PATTERN
# ----------------------
@app.post("/verify-pattern")
def verify_pattern(request: PatternVerifyRequest):
    """
    Checks if the provided pattern exactly matches the stored pattern.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT pattern
            FROM users
            WHERE username = ?
            """,
            (request.username,),
        )
        db_user = cursor.fetchone()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    stored_pattern = decrypt_pattern(db_user["pattern"])
    if stored_pattern == request.pattern:
        return {"message": "Pattern verified"}

    raise HTTPException(status_code=401, detail="Incorrect pattern")

# ----------------------
# 5) UPDATE PATTERN
# ----------------------
@app.post("/update-pattern/")
def update_pattern(request: PatternUpdateRequest):
    """
    If a user wants to set or change their pattern.
    - If the user is brand new, their pattern might be [0..0].
    - If the pattern is the same as the old one, error out.
    - If successfully changed, set status = True and update last_pattern_update.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT pattern, status
            FROM users
            WHERE username = ?
            """,
            (request.username,),
        )
        db_user = cursor.fetchone()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        current_pattern = decrypt_pattern(db_user["pattern"])
        # If new pattern is the same, that's an error
        if current_pattern == request.pattern:
            raise HTTPException(
                status_code=400,
                detail="New pattern cannot be the same as the old pattern",
            )

        # Encrypt new pattern
        encrypted_pattern = encrypt_pattern(request.pattern)
        new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # IMPORTANT:
        # set status = true (1) because user is now "valid" again
        cursor.execute(
            """
            UPDATE users
            SET pattern = ?, last_pattern_update = ?, status = 1
            WHERE username = ?
            """,
            (encrypted_pattern, new_timestamp, request.username),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Pattern updated successfully"}

# ----------------------
# 6) LAST UPDATE
# ----------------------
@app.get("/last-update/{username}")
def get_last_update(username: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT last_pattern_update
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        user = cursor.fetchone()

    if not user or not user["last_pattern_update"]:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": username,
        "last_pattern_update": user["last_pattern_update"]
    }

