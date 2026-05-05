import os
import hmac
import hashlib
from flask import Blueprint, request, jsonify

from app.core.database import get_connection, create_user

webhook_bp = Blueprint("webhook", __name__)

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")


# =========================
# 🔐 VERIFY SIGNATURE
# =========================
def verify_signature(payload: bytes, signature: str) -> bool:
    if not PAYSTACK_SECRET or not signature:
        return False

    computed_hash = hmac.new(
        PAYSTACK_SECRET.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    return hmac.compare_digest(computed_hash, signature)


# =========================
# 💳 WEBHOOK
# =========================
@webhook_bp.route("/paystack", methods=["POST"])
def paystack_webhook():

    payload = request.get_data()
    signature = request.headers.get("x-paystack-signature")

    # 🔐 security check
    if not verify_signature(payload, signature):
        return jsonify({"error": "invalid signature"}), 403

    event = request.get_json()

    if not event or event.get("event") != "charge.success":
        return jsonify({"status": "ignored"}), 200

    data = event["data"]

    reference = data.get("reference")
    amount = data.get("amount", 0) / 100

    # =========================
    # SAFE USER EXTRACTION
    # from metadata (BEST PRACTICE)
    # =========================
    metadata = data.get("metadata", {})
    user_id = metadata.get("telegram_id")

    # fallback (legacy email format support)
    if not user_id:
        email = data.get("customer", {}).get("email", "")
        if "user" in email:
            try:
                user_id = email.split("user")[1].split("@")[0]
            except Exception:
                return jsonify({"error": "invalid user format"}), 400

    if not reference or not user_id:
        return jsonify({"error": "invalid payload"}), 400

    conn = get_connection()
    cur = conn.cursor()

    try:
        # =========================
        # PREVENT DOUBLE CREDIT
        # =========================
        cur.execute(
            "SELECT 1 FROM transactions WHERE reference = %s",
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
            (amount, str(user_id))
        )

        # =========================
        # LOG TRANSACTION
        # =========================
        cur.execute(
            """
            INSERT INTO transactions (user_id, reference, amount, type, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (str(user_id), reference, amount, "credit", "success")
        )

        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

    return jsonify({
        "status": "success",
        "credited": amount,
        "user_id": user_id
    }), 200