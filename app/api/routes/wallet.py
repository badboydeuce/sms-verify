from flask import Blueprint, request, jsonify
from app.services.paystack import PaystackService
from app.services.payment_store import PaymentStore

wallet_bp = Blueprint("wallet", __name__)

paystack = PaystackService()
payments = PaymentStore()


@wallet_bp.route("/fund", methods=["POST"])
def fund_wallet():
    data = request.json

    user_id = data.get("user_id")
    amount = float(data.get("amount"))
    email = data.get("email")

    res = paystack.initialize(email, amount, user_id)

    if not res.get("status"):
        return jsonify({"success": False}), 400

    reference = res["data"]["reference"]

    # store payment
    payments.save(reference, user_id, amount)

    return jsonify({
        "success": True,
        "authorization_url": res["data"]["authorization_url"]
    })
