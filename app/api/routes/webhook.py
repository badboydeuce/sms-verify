# app/api/routes/webhook.py

import hmac
import hashlib
import json
import hmac

from flask import Blueprint, request, jsonify

from app.core.config import settings
from app.services.wallet import WalletService

webhook_bp = Blueprint("webhook", __name__)
wallet = WalletService()


# =========================
# 🔐 PAYSTACK WEBHOOK (FIXED)
# =========================
@webhook_bp.route("/paystack", methods=["POST"])
def paystack_webhook():

    payload = request.data
    signature = request.headers.get("x-paystack-signature")

    # =========================
    # 🔐 VERIFY SIGNATURE (SECURE)
    # =========================
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed, signature or ""):
        return jsonify({"error": "invalid signature"}), 403

    # =========================
    # 📦 SAFE JSON PARSE
    # =========================
    try:
        event = json.loads(payload.decode("utf-8"))
    except Exception:
        return jsonify({"error": "invalid payload"}), 400

    event_type = event.get("event")
    data = event.get("data", {})

    # =========================
    # 💰 HANDLE SUCCESS PAYMENT
    # =========================
    if event_type == "charge.success":

        metadata = data.get("metadata", {})
        user_id = metadata.get("telegram_id")
        amount = data.get("amount", 0) / 100
        reference = data.get("reference")

        if not user_id or not reference:
            return jsonify({"status": "missing metadata"}), 400

        # =========================
        # 💳 CREDIT WALLET
        # =========================
        wallet.add_balance(user_id, amount, reference)

    # =========================
    # ⚠️ IGNORE OTHER EVENTS SAFELY
    # =========================
    return jsonify({"status": "ok"})
