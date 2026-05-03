# app/services/wallet_service.py

from app.database import get_connection
import logging

logger = logging.getLogger(__name__)


class WalletService:

    def __init__(self):
        self._init_db()

    # =========================
    # 🧱 INIT TABLE
    # =========================
    def _init_db(self):
        conn = get_connection()
        cur = conn.cursor()

        # USERS TABLE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance REAL DEFAULT 0
        )
        """)

        # TRANSACTIONS TABLE (VERY IMPORTANT)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            reference TEXT UNIQUE,
            amount REAL,
            type TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    # =========================
    # 💰 GET BALANCE
    # =========================
    def get_balance(self, user_id: str) -> float:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return 0.0

        return row["balance"]

    # =========================
    # ➕ ADD BALANCE (SAFE)
    # =========================
    def add_balance(self, user_id: str, amount: float, reference: str = None):

        conn = get_connection()
        cur = conn.cursor()

        try:
            # 🔥 prevent duplicate Paystack credits
            if reference:
                cur.execute(
                    "SELECT 1 FROM transactions WHERE reference=?",
                    (reference,)
                )
                if cur.fetchone():
                    logger.warning("Duplicate transaction blocked")
                    return False

            # create user if not exists
            cur.execute("""
            INSERT OR IGNORE INTO users (user_id, balance)
            VALUES (?, 0)
            """, (user_id,))

            # update balance
            cur.execute("""
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?
            """, (amount, user_id))

            # log transaction
            cur.execute("""
            INSERT INTO transactions (user_id, reference, amount, type, status)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, reference, amount, "credit", "success"))

            conn.commit()
            return True

        except Exception as e:
            logger.exception(e)
            return False

        finally:
            conn.close()

    # =========================
    # ➖ DEDUCT BALANCE
    # =========================
    def deduct_balance(self, user_id: str, amount: float, reference: str = None) -> bool:

        conn = get_connection()
        cur = conn.cursor()

        try:
            balance = self.get_balance(user_id)

            if balance < amount:
                return False

            cur.execute("""
            UPDATE users
            SET balance = balance - ?
            WHERE user_id = ?
            """, (amount, user_id))

            cur.execute("""
            INSERT INTO transactions (user_id, reference, amount, type, status)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, reference, amount, "debit", "success"))

            conn.commit()
            return True

        except Exception as e:
            logger.exception(e)
            return False

        finally:
            conn.close()