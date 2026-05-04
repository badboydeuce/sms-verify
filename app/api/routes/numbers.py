# app/api/routes/numbers.py

PRICE_PER_NUMBER = 3500  # ₦150 (you can change)

from flask import Blueprint, request, jsonify
from app.services.smsman import SMSManProvider

from app.services.wallet import WalletService

wallet = WalletService()

numbers_bp = Blueprint("numbers", __name__)

sms = SMSManProvider()


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
    return jsonify(sms.get_services(country_id))


# =========================
# 📞 BUY NUMBER
# =========================
@numbers_bp.route("/buy", methods=["POST"])
def buy_number():
    data = request.json

    country = data.get("country")
    service = data.get("service")
    user_id = str(data.get("user_id"))

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
    deducted = wallet.debit(user_id, price)

    if not deducted:
        return jsonify({
            "success": False,
            "error": "Failed to deduct balance"
        }), 400

    # =========================
    # 📞 BUY FROM SMS-MAN
    # =========================
    result = sms.get_number(country, service)

    # =========================
    # ❌ IF FAILED → REFUND
    # =========================
    if not result or result.get("error"):
        wallet.credit(user_id, price)

        return jsonify({
            "success": False,
            "error": "Number purchase failed. Refunded."
        }), 400

    # =========================
    # ✅ SUCCESS
    # =========================
    return jsonify({
        "success": True,
        "request_id": result["request_id"],
        "number": result["number"]
    })
