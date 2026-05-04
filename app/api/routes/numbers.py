# app/api/routes/numbers.py

from flask import Blueprint, request, jsonify

from app.services.smsman import SMSManProvider
from app.services.wallet import WalletService

numbers_bp = Blueprint("numbers", __name__)

sms = SMSManProvider()
wallet = WalletService()

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

    return jsonify(sms.get_services())


# =========================
# 📞 BUY NUMBER (FIXED)
# =========================
@numbers_bp.route("/buy", methods=["POST"])
def buy_number():

    data = request.json or {}

    country = data.get("country")
    service = data.get("service")
    user_id = str(data.get("user_id"))

    if not country or not service or not user_id:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    # convert safely
    try:
        country = int(country)
        service = int(service)
    except ValueError:
        return jsonify({"success": False, "error": "Invalid country/service ID"}), 400

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
    # 📞 CALL SMS PROVIDER
    # =========================
    result = sms.get_number(country, service)

    # ❌ PROVIDER ERROR (DO NOT CHARGE USER)
    if isinstance(result, dict) and result.get("error"):
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 400

    # =========================
    # ➖ DEDUCT BALANCE (ONLY AFTER SUCCESS)
    # =========================
    deducted = wallet.deduct_balance(user_id, price)

    if not deducted:
        return jsonify({
            "success": False,
            "error": "Wallet deduction failed"
        }), 500

    # =========================
    # ⚠️ SAFETY CHECK
    # =========================
    if not result.get("request_id") or not result.get("number"):
        wallet.add_balance(user_id, price)

        return jsonify({
            "success": False,
            "error": "Invalid provider response. Refunded."
        }), 500

    # =========================
    # ✅ SUCCESS
    # =========================
    return jsonify({
        "success": True,
        "request_id": result["request_id"],
        "number": result["number"]
    })
