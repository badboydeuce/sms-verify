import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings


# =========================
# CONNECTION
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

    # USERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance NUMERIC DEFAULT 0,
            active_numbers INTEGER DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # TRANSACTIONS TABLE
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

    # ACTIVATIONS TABLE
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


# =========================
# 👤 GET USER
# =========================
def get_user(user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE user_id = %s",
        (str(user_id),)
    )

    user = cur.fetchone()
    conn.close()

    return user


# =========================
# 🆕 CREATE USER (SAFE)
# =========================
def create_user(user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (user_id, balance)
        VALUES (%s, 0)
        ON CONFLICT (user_id) DO NOTHING
    """, (str(user_id),))

    conn.commit()
    conn.close()

    return get_user(user_id)