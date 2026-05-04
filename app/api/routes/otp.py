# app/api/routes/otp.py

from flask import Blueprint, jsonify
from app.services.smsman import SMSManProvider

otp_bp = Blueprint("otp", __name__)

sms = SMSManProvider()


# =========================
# 📩 CHECK OTP (FIXED)
# =========================
@otp_bp.route("/check/<request_id>", methods=["GET"])
def check_otp(request_id):

    result = sms.get_sms(request_id)

    # ⏳ still waiting
    if result.get("status") == "pending":
        return jsonify({"status": "waiting"})

    # ❌ API error
    if result.get("status") == "error":
        return jsonify({
            "status": "error",
            "message": result.get("error", "Unknown error")
        }), 400

    # ✅ OTP received
    if result.get("status") == "received":
        return jsonify({
            "status": "received",
            "otp": result.get("otp")
        })

    # ⚠️ fallback safety
    return jsonify({"status": "unknown"})
