# app/api/routes/otp.py

from flask import Blueprint, request, jsonify
from app.services.smsman import SMSManProvider

otp_bp = Blueprint("otp", __name__)

sms = SMSManProvider()


# =========================
# 📩 CHECK OTP
# =========================
@otp_bp.route("/check/<request_id>", methods=["GET"])
def check_otp(request_id):

    result = sms.get_sms(request_id)

    if result.get("status") == "pending":
        return jsonify({"status": "waiting"})

    if result.get("status") == "received":
        return jsonify({
            "status": "received",
            "otp": result["code"]
        })

    return jsonify({"status": "error"})
