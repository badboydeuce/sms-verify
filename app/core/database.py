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
