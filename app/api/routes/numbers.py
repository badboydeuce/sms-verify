# app/api/routes/numbers.py

from flask import Blueprint, request, jsonify
from app.services.smsman import SMSManProvider

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
    user_id = data.get("user_id")

    result = sms.get_number(country, service)

    if "error" in result:
        return jsonify(result), 400

    return jsonify({
        "success": True,
        "user_id": user_id,
        "request_id": result["request_id"],
        "number": result["number"]
    })
