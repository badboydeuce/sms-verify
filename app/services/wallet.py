# app/services/wallet.py

from app.core.database import get_connection


class WalletService:

    # =========================
    # 💰 GET BALANCE
    # =========================
    def get_balance(self, user_id: str):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT balance FROM users WHERE user_id=%s", (user_id,))
        row = cur.fetchone()

        conn.close()

        return row["balance"] if row else 0

    # =========================
    # ➕ CREDIT WALLET
    # =========================
    def credit(self, user_id: str, amount: float, reference: str = None):

        conn = get_connection()
        cur = conn.cursor()

        # prevent duplicate credit
        if reference:
            cur.execute(
                "SELECT 1 FROM transactions WHERE reference=%s",
                (reference,)
            )
            if cur.fetchone():
                return False

        cur.execute(
            "INSERT INTO users (user_id, balance) VALUES (%s, 0) ON CONFLICT (user_id) DO NOTHING",
            (user_id,)
        )

        cur.execute(
            "UPDATE users SET balance = balance + %s WHERE user_id=%s",
            (amount, user_id)
        )

        cur.execute("""
            INSERT INTO transactions (user_id, reference, amount, type, status)
            VALUES (%s, %s, %s, 'credit', 'success')
        """, (user_id, reference, amount))

        conn.commit()
        conn.close()

        return True

    # =========================
    # ➖ DEBIT WALLET
    # =========================
    def debit(self, user_id: str, amount: float):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT balance FROM users WHERE user_id=%s", (user_id,))
        row = cur.fetchone()

        if not row or row["balance"] < amount:
            conn.close()
            return False

        cur.execute(
            "UPDATE users SET balance = balance - %s WHERE user_id=%s",
            (amount, user_id)
        )

        cur.execute("""
            INSERT INTO transactions (user_id, reference, amount, type, status)
            VALUES (%s, NULL, %s, 'debit', 'success')
        """, (user_id, amount))

        conn.commit()
        conn.close()

        return True
