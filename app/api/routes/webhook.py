import os
import hmac
import hashlib
from flask import Blueprint, request, jsonify

from app.core.database import get_connection, create_user

webhook_bp = Blueprint("webhook", __name__)

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")


# =========================
# 🔐 VERIFY PAYSTACK SIGNATURE
# =========================
def verify_signature(payload: bytes, signature: str) -> bool:

    if not signature:
        return False

    computed_hash = hmac.new(
        PAYSTACK_SECRET.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    return hmac.compare_digest(computed_hash, signature)


# =========================
# 💳 PAYSTACK WEBHOOK ROUTE
# =========================
@webhook_bp.route("/paystack", methods=["POST"])
def paystack_webhook():

    payload = request.get_data()
    signature = request.headers.get("x-paystack-signature")

    # 🔐 security check
    if not verify_signature(payload, signature):
        return jsonify({"error": "invalid signature"}), 403

    event = request.json

    # only handle successful payments
    if event.get("event") != "charge.success":
        return jsonify({"status": "ignored"}), 200

    data = event["data"]

    reference = data.get("reference")
    amount = data.get("amount", 0) / 100
    email = data.get("customer", {}).get("email")

    if not reference or not email:
        return jsonify({"error": "invalid payload"}), 400

    # =========================
    # EXTRACT USER ID FROM EMAIL
    # (your system format: user123@deuce.com)
    # =========================
    try:
        user_id = email.split("user")[1].split("@")[0]
    except Exception:
        return jsonify({"error": "invalid user email format"}), 400

    conn = get_connection()
    cur = conn.cursor()

    # =========================
    # PREVENT DOUBLE CREDIT
    # =========================
    cur.execute(
        "SELECT id FROM transactions WHERE reference = %s",
        (reference,)
    )

    if cur.fetchone():
        conn.close()
        return jsonify({"status": "duplicate"}), 200

    # =========================
    # ENSURE USER EXISTS
    # =========================
    create_user(user_id)

    # =========================
    # CREDIT WALLET
    # =========================
    cur.execute(
        """
        UPDATE users
        SET balance = balance + %s
        WHERE user_id = %s
        """,
        (amount, user_id)
    )

    # =========================
    # LOG TRANSACTION
    # =========================
    cur.execute(
        """
        INSERT INTO transactions (user_id, reference, amount, type, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, reference, amount, "credit", "success")
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "credited": amount,
        "user_id": user_id
    }), 200