# app/api/routes/wallet.py

from flask import Blueprint, request, jsonify
from app.services.wallet import WalletService

wallet_bp = Blueprint("wallet", __name__)

wallet = WalletService()


# =========================
# 💰 GET BALANCE
# =========================
@wallet_bp.route("/balance/<user_id>", methods=["GET"])
def balance(user_id):
    return jsonify({
        "user_id": user_id,
        "balance": wallet.get_balance(user_id)
    })


# =========================
# ➕ ADD BALANCE (manual test)
# =========================
@wallet_bp.route("/credit", methods=["POST"])
def credit():
    data = request.json

    success = wallet.add_balance(
        user_id=data["user_id"],
        amount=data["amount"],
        reference=data.get("reference")
    )

    return jsonify({"success": success})
