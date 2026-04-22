import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .models import AUDIT_GRADES, AUDIT_STATUSES, RISK_LEVELS
from .seed import SAMPLE_AUDITS


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "audit_system.db"


def get_database_path() -> Path:
    configured_path = os.getenv("AUDIT_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return DEFAULT_DB_PATH


def ensure_database_directory() -> Path:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection() -> sqlite3.Connection:
    db_path = ensure_database_directory()
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def db_cursor():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        yield connection, cursor
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with db_cursor() as (_, cursor):
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'viewer')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                department TEXT NOT NULL,
                observation TEXT NOT NULL,
                risk TEXT NOT NULL CHECK(risk IN ({",".join(repr(item) for item in RISK_LEVELS)})),
                grade TEXT NOT NULL CHECK(grade IN ({",".join(repr(item) for item in AUDIT_GRADES)})),
                action TEXT NOT NULL,
                owner TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ({",".join(repr(item) for item in AUDIT_STATUSES)})),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def seed_audits_if_empty() -> None:
    with db_cursor() as (_, cursor):
        audit_count = cursor.execute("SELECT COUNT(*) AS count FROM audits").fetchone()["count"]
        if audit_count > 0:
            return
        cursor.executemany(
            """
            INSERT INTO audits (
                title, department, observation, risk, grade, action, owner, due_date, status
            ) VALUES (
                :title, :department, :observation, :risk, :grade, :action, :owner, :due_date, :status
            )
            """,
            SAMPLE_AUDITS,
        )
