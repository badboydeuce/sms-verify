from app.services.database import get_connection


class WalletService:

    def __init__(self):
        self._init_db()

    def _init_db(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0
        )
        """)

        conn.commit()
        conn.close()

    # =========================
    # 💰 GET BALANCE
    # =========================
    def get_balance(self, user_id: int) -> float:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()

        if not row:
            cur.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
            conn.commit()
            conn.close()
            return 0.0

        conn.close()
        return row[0]

    # =========================
    # ➕ ADD BALANCE
    # =========================
    def add_balance(self, user_id: int, amount: float):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO users (user_id, balance)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET balance = balance + ?
        """, (user_id, amount, amount))

        conn.commit()
        conn.close()

    # =========================
    # ➖ DEDUCT BALANCE
    # =========================
    def deduct_balance(self, user_id: int, amount: float) -> bool:
        balance = self.get_balance(user_id)

        if balance < amount:
            return False

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        UPDATE users SET balance = balance - ?
        WHERE user_id = ?
        """, (amount, user_id))

        conn.commit()
        conn.close()

        return True
