import time
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings


def get_connection(retries=3):
    if not settings.DATABASE_URL:
        raise Exception("DATABASE_URL is not set")

    for i in range(retries):
        try:
            return psycopg2.connect(
                settings.DATABASE_URL,
                cursor_factory=RealDictCursor,
                sslmode="require"
            )
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(2)


# =========================
# HELPERS
# =========================
def fetch_one(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchone()
    conn.close()
    return data


def execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


# =========================
# INIT DB
# =========================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance NUMERIC DEFAULT 0,
            active_numbers INTEGER DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


# =========================
# USER FUNCTIONS
# =========================
def get_user(user_id):
    return fetch_one(
        "SELECT * FROM users WHERE user_id=%s",
        (str(user_id),)
    )


def create_user(user_id):
    execute(
        """
        INSERT INTO users (user_id, balance)
        VALUES (%s, 0)
        ON CONFLICT DO NOTHING
        """,
        (str(user_id),)
    )
    return get_user(user_id)


# =========================
# WALLET OPS
# =========================
def credit_user(user_id, amount):
    execute(
        "UPDATE users SET balance = balance + %s WHERE user_id=%s",
        (amount, str(user_id))
    )


def debit_user(user_id, amount):
    execute(
        "UPDATE users SET balance = balance - %s WHERE user_id=%s AND balance >= %s",
        (amount, str(user_id), amount)
    )