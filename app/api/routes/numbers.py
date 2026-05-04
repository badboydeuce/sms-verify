# app/api/routes/numbers.py

from flask import Blueprint, request, jsonify

from app.services.smsman import SMSManProvider
from app.services.wallet import WalletService

numbers_bp = Blueprint("numbers", __name__)

sms = SMSManProvider()
wallet = WalletService()

# 💰 Price per number (profit margin control)
PRICE_PER_NUMBER = 3500


# =========================
# 🌍 GET COUNTRIES
# =========================
@numbers_bp.route("/countries", methods=["GET"])
def countries():
    return jsonify(sms.get_countries())


# =========================
# 📱 GET SERVICES
# =========================
@numbers_bp.route("/services", methods=["GET"])
def services():
    country_id = request.args.get("country_id")

    if not country_id:
        return jsonify({"error": "country_id required"}), 400

    return jsonify(sms.get_services(country_id))


# =========================
# 📞 BUY NUMBER (WITH WALLET DEDUCTION)
# =========================
@numbers_bp.route("/buy", methods=["POST"])
def buy_number():
    data = request.json

    country = data.get("country")
    service = data.get("service")
    user_id = str(data.get("user_id"))

    if not country or not service or not user_id:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    price = PRICE_PER_NUMBER

    # =========================
    # 💰 CHECK BALANCE
    # =========================
    balance = wallet.get_balance(user_id)

    if balance < price:
        return jsonify({
            "success": False,
            "error": "Insufficient balance"
        }), 400

    # =========================
    # ➖ DEDUCT BALANCE
    # =========================
    deducted = wallet.deduct_balance(user_id, price)

    if not deducted:
        return jsonify({
            "success": False,
            "error": "Wallet deduction failed"
        }), 400

    # =========================
    # 📞 CALL SMS PROVIDER
    # =========================
    result = sms.get_number(country, service)

    # =========================
    # ❌ FAILURE → REFUND
    # =========================
    if not result or result.get("error"):
        wallet.add_balance(user_id, price)

        return jsonify({
            "success": False,
            "error": "Number purchase failed. Amount refunded."
        }), 400

    # =========================
    # ✅ SUCCESS
    # =========================
    return jsonify({
        "success": True,
        "request_id": result["request_id"],
        "number": result["number"]
    })
