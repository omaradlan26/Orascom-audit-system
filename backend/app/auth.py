import hashlib
import os
import secrets
from datetime import datetime
from functools import wraps
from typing import Any

from fastapi import Depends, Header, HTTPException, status

from .db import db_cursor


SESSION_STORE: dict[str, dict[str, str]] = {}


def hash_password(password: str, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), password_salt.encode("utf-8"), 100_000)
    return f"{password_salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, current_hash = stored_hash.split("$", maxsplit=1)
    except ValueError:
        return False
    candidate_hash = hash_password(password, salt).split("$", maxsplit=1)[1]
    return secrets.compare_digest(candidate_hash, current_hash)


def bootstrap_admin_user() -> None:
    username = os.getenv("AUDIT_ADMIN_USERNAME", "admin")
    password = os.getenv("AUDIT_ADMIN_PASSWORD", "admin123")
    password_hash = hash_password(password)

    with db_cursor() as (_, cursor):
        existing_admin = cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if existing_admin:
            return
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, "admin"),
        )


def create_session(username: str, role: str) -> str:
    token = secrets.token_urlsafe(32)
    SESSION_STORE[token] = {
        "username": username,
        "role": role,
        "issued_at": datetime.utcnow().isoformat(),
    }
    return token


def delete_session(token: str) -> None:
    SESSION_STORE.pop(token, None)


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    return token


def get_current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    token = _extract_bearer_token(authorization)
    session = SESSION_STORE.get(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    return {"token": token, **session}


def require_admin(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
