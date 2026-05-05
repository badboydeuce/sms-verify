import os
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings


# =========================
# CONNECTION (MUST BE FIRST)
# =========================
def get_connection():
    if not settings.DATABASE_URL:
        raise Exception("DATABASE_URL is not set")

    return psycopg2.connect(
        settings.DATABASE_URL,
        cursor_factory=RealDictCursor
    )


# =========================
# INIT DB
# =========================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance NUMERIC DEFAULT 0
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            reference TEXT UNIQUE,
            amount NUMERIC,
            type TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS activations (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            country TEXT,
            service TEXT,
            request_id TEXT UNIQUE,
            number TEXT,
            otp TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

    print("✅ Database initialized")
