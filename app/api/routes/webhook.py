# app/api/routes/webhook.py

import hmac
import hashlib
from flask import Blueprint, request, jsonify

from app.core.config import settings
from app.services.wallet import WalletService

webhook_bp = Blueprint("webhook", __name__)
wallet = WalletService()


# =========================
# 🔐 PAYSTACK WEBHOOK
# =========================
@webhook_bp.route("/paystack", methods=["POST"])
def paystack_webhook():

    signature = request.headers.get("x-paystack-signature")
    payload = request.data

    # VERIFY SIGNATURE (CRITICAL SECURITY)
    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if computed != signature:
        return jsonify({"error": "invalid signature"}), 403

    event = request.json

    if event["event"] == "charge.success":
        data = event["data"]

        user_id = data["metadata"]["telegram_id"]
        amount = data["amount"] / 100
        reference = data["reference"]

        wallet.add_balance(user_id, amount, reference)

    return jsonify({"status": "ok"})
