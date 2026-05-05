# =========================
# USER HELPERS
# =========================

def get_user(user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE user_id = %s;",
        (str(user_id),)
    )

    user = cur.fetchone()

    conn.close()
    return user


def create_user(user_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (user_id, balance)
        VALUES (%s, 0)
        ON CONFLICT (user_id) DO NOTHING
        RETURNING *;
        """,
        (str(user_id),)
    )

    user = cur.fetchone()

    # If user already existed, fetch it
    if not user:
        cur.execute(
            "SELECT * FROM users WHERE user_id = %s;",
            (str(user_id),)
        )
        user = cur.fetchone()

    conn.commit()
    conn.close()

    return user

# =========================
# 🛠 INIT DATABASE
# =========================

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance NUMERIC DEFAULT 0
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
