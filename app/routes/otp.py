# app/routes/otp.py

from flask import Blueprint, request, jsonify
import requests
import os
import time

otp_bp = Blueprint("otp", __name__)

SMS_MAN_API_KEY = os.getenv("SMS_MAN_API_KEY")
BASE_URL = "https://api.sms-man.com/control"

# Import shared storage
from app.routes.numbers import activations

EXPIRY_TIME = 300  # 5 minutes


# ----------------------------
# Check OTP (manual or auto)
# ----------------------------
@otp_bp.route("/check/<activation_id>", methods=["GET"])
def check_otp(activation_id):

    if activation_id not in activations:
        return jsonify({"error": "Invalid activation ID"}), 404

    activation = activations[activation_id]

    # Check expiry
    if time.time() - activation["created_at"] > EXPIRY_TIME:
        activation["status"] = "expired"
        return jsonify({
            "status": "expired",
            "message": "Number expired. Refund user."
        })

    url = f"{BASE_URL}/get-sms?token={SMS_MAN_API_KEY}&request_id={activation_id}"
    res = requests.get(url).json()

    # No SMS yet
    if res.get("sms_code") is None:
        return jsonify({
            "status": "waiting"
        })

    # OTP received
    activation["status"] = "completed"
    activation["otp"] = res["sms_code"]

    return jsonify({
        "status": "received",
        "otp": res["sms_code"]
    })