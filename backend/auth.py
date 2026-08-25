"""
LearnLens AI - Authentication Utilities
JWT token management + password hashing
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "learnlens-hackathon-secret-key-2024")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Simple SHA256 hashing for hackathon demo (no bcrypt dependency issues)
_HASH_SALT = "learnlens-salt-2024"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    expected = hashlib.sha256(f"{_HASH_SALT}{plain_password}".encode()).hexdigest()
    return secrets.compare_digest(expected, hashed_password)


def get_password_hash(password: str) -> str:
    return hashlib.sha256(f"{_HASH_SALT}{password}".encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
