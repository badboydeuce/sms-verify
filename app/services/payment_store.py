from app.core.database import get_connection


class PaymentStore:

    def __init__(self):
        self._init_db()

    def _init_db(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            reference TEXT PRIMARY KEY,
            user_id TEXT,
            amount REAL,
            status TEXT DEFAULT 'pending'
        )
        """)

        conn.commit()
        conn.close()

    def save(self, reference: str, user_id: str, amount: float):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT OR REPLACE INTO payments (reference, user_id, amount)
        VALUES (?, ?, ?)
        """, (reference, user_id, amount))

        conn.commit()
        conn.close()

    def get(self, reference: str):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT user_id, amount FROM payments WHERE reference=?
        """, (reference,))

        row = cur.fetchone()
        conn.close()

        return row

    def mark_success(self, reference: str):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        UPDATE payments SET status='success'
        WHERE reference=?
        """, (reference,))

        conn.commit()
        conn.close()
