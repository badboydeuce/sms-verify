from flask import Flask, request, jsonify
import requests
import logging

from app.config import settings
from app.services.wallet_service import WalletService
from app.services.payment_store import PaymentStore

app = Flask(__name__)

logger = logging.getLogger(__name__)

wallet = WalletService()
payments = PaymentStore()


# =========================
# 🔗 PAYSTACK CALLBACK ROUTE
# =========================
@app.route('/paystack/verify', methods=['GET'])
def paystack_callback():
    reference = request.args.get('reference')

    if not reference:
        return jsonify({"error": "Invalid reference"}), 400

    # =========================
    # 🔍 VERIFY PAYMENT
    # =========================
    result = verify_transaction(reference)

    if not result.get("success"):
        return jsonify({"error": "Payment verification failed"}), 400

    user_id, amount = payments.get_user(reference) or (None, None)

    if not user_id:
        return jsonify({"error": "User not found"}), 404

    # =========================
    # 🛡️ AVOID DOUBLE CREDIT
    # =========================
    if is_already_processed(reference):
        return jsonify({"message": "Already processed"}), 200

    # =========================
    # 💰 CREDIT WALLET
    # =========================
    wallet.add_balance(user_id, amount)

    payments.mark_success(reference)

    notify_user(user_id, amount)

    return jsonify({
        "status": "success",
        "message": "Wallet credited",
        "amount": amount
    }), 200


# =========================
# 🔍 VERIFY TRANSACTION
# =========================
def verify_transaction(reference: str):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        res = requests.get(url, headers=headers, timeout=15)
        data = res.json()

        if data.get("status") and data["data"]["status"] == "success":
            return {
                "success": True,
                "amount": data["data"]["amount"] / 100
            }

        return {"success": False}

    except Exception as e:
        logger.error(f"Verify error: {e}")
        return {"success": False}


# =========================
# 🛡️ IDEMPOTENCY CHECK
# =========================
def is_already_processed(reference: str) -> bool:
    from app.services.database import get_connection

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT status FROM payments WHERE reference=?", (reference,))
    row = cur.fetchone()

    conn.close()

    return row and row[0] == "success"


# =========================
# 📲 NOTIFY USER
# =========================
def notify_user(user_id: int, amount: float):
    try:
        from telegram import Bot

        bot = Bot(token=settings.BOT_TOKEN)

        bot.send_message(
            chat_id=user_id,
            text=(
                "✅ *Payment Successful!*\n\n"
                f"💰 ₦{amount:,.2f} has been added to your wallet."
            ),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Telegram notify failed: {e}")


# =========================
# 🚀 RUN (DEV ONLY)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
