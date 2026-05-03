# app/routes/numbers.py

from flask import Blueprint, request, jsonify
import requests
import os
import time

numbers_bp = Blueprint("numbers", __name__)

SMS_MAN_API_KEY = os.getenv("SMS_MAN_API_KEY")
BASE_URL = "https://api.sms-man.com/control"

# Temporary storage (replace with DB later)
activations = {}

# ----------------------------
# Get Countries
# ----------------------------
@numbers_bp.route("/countries", methods=["GET"])
def get_countries():
    url = f"{BASE_URL}/get-countries?token={SMS_MAN_API_KEY}"
    res = requests.get(url).json()

    return jsonify(res)


# ----------------------------
# Get Services by Country
# ----------------------------
@numbers_bp.route("/services", methods=["GET"])
def get_services():
    country = request.args.get("country")

    url = f"{BASE_URL}/get-services?token={SMS_MAN_API_KEY}&country_id={country}"
    res = requests.get(url).json()

    return jsonify(res)


# ----------------------------
# Buy Number
# ----------------------------
@numbers_bp.route("/buy", methods=["POST"])
def buy_number():
    data = request.json
    country = data.get("country")
    service = data.get("service")
    user_id = data.get("user_id")

    url = f"{BASE_URL}/get-number?token={SMS_MAN_API_KEY}&country_id={country}&application_id={service}"
    res = requests.get(url).json()

    if res.get("error_code"):
        return jsonify({"error": res}), 400

    activation_id = res["request_id"]
    number = res["number"]

    # Save activation
    activations[activation_id] = {
        "user_id": user_id,
        "number": number,
        "service": service,
        "country": country,
        "status": "waiting",
        "created_at": time.time()
    }

    return jsonify({
        "activation_id": activation_id,
        "number": number
    })