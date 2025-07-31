# dagster_webserver/db_auth.py

import os
import psycopg2
import hashlib
import secrets
from dagster_webserver.user import User
from typing import Optional, Tuple

# Database connection details
DB_HOST = os.getenv("DAGSTER_POSTGRES_HOSTNAME")
DB_NAME = os.getenv("DAGSTER_POSTGRES_DB")
DB_USER = os.getenv("DAGSTER_POSTGRES_USER")
DB_PASSWORD = os.getenv("DAGSTER_POSTGRES_PASSWORD")

# Hashing Configuration
HASH_ALGORITHM, ITERATIONS, SALT_SIZE, KEY_LENGTH = 'sha256', 260000, 16, 32

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def get_password_hash(password: str) -> str:
    salt = secrets.token_bytes(SALT_SIZE)
    key = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode('utf-8'), salt, ITERATIONS, dklen=KEY_LENGTH)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(plain_password: str, stored_hash_with_salt: str) -> bool:
    try:
        salt_hex, stored_hashed_password_hex = stored_hash_with_salt.split(':')
        salt, key = bytes.fromhex(salt_hex), bytes.fromhex(stored_hashed_password_hex)
        new_key = hashlib.pbkdf2_hmac(HASH_ALGORITHM, plain_password.encode('utf-8'), salt, ITERATIONS, dklen=KEY_LENGTH)
        return secrets.compare_digest(new_key, key)
    except Exception:
        return False

def _ensure_users_table_exists(cur):
    """A helper function to create the users table if it does not exist."""
    print("Ensuring 'users' table exists...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("Table 'users' is present.")

def create_standard_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Creates a new user in the standard database.
    It will also create the 'users' table on the first run if it doesn't exist.
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # === CRITICAL CHANGE: ENSURE TABLE EXISTS BEFORE DOING ANYTHING ELSE ===
        _ensure_users_table_exists(cur)
        
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return (False, "User already exists.")
        
        hashed_password = get_password_hash(password)
        email = f"{username}@npci.org.in"
        cur.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
            (username, hashed_password, email)
        )
        conn.commit()
        return (True, "User created successfully!")
    except Exception as e:
        if conn:
            conn.rollback()
        return (False, f"Database error during creation: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def authenticate_standard_user(username: str, password: str) -> Optional[User]:
    """Authenticates a user against the standard database."""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result:
            return None # User not found
        
        stored_hash_with_salt = result[0]
        if not verify_password(password, stored_hash_with_salt):
            return None # Incorrect password
            
        return User(identifier=hash(username), username=username,password=password)
    except psycopg2.errors.UndefinedTable:
        # This handles the case where someone tries to log in before anyone has signed up.
        print("Login failed: 'users' table does not exist. Please sign up a user first to create it.")
        return None
    except Exception as e:
        print(f"Error during standard user authentication: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()