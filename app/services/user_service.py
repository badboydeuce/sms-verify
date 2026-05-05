from app.database import get_connection


class UserService:

    # =========================
    # GET USER
    # =========================
    def get_user(self, telegram_id: str):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )

        user = cur.fetchone()
        conn.close()

        return user


    # =========================
    # GET BALANCE
    # =========================
    def get_balance(self, telegram_id: str):

        user = self.get_user(telegram_id)

        if not user:
            return 0

        return user["wallet_balance"]


    # =========================
    # TOTAL PURCHASES
    # =========================
    def get_total_purchases(self, telegram_id: str):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*) as total
            FROM transactions
            WHERE telegram_id = ? AND type = 'purchase'
        """, (telegram_id,))

        result = cur.fetchone()
        conn.close()

        return result["total"] if result else 0


    # =========================
    # ACTIVE NUMBERS (BASIC VERSION)
    # =========================
    def get_active_numbers(self, telegram_id: str):

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*) as active
            FROM transactions
            WHERE telegram_id = ?
            AND type = 'purchase'
            AND status = 'active'
        """, (telegram_id,))

        result = cur.fetchone()
        conn.close()

        return result["active"] if result else 0
