from flask import Blueprint, request, jsonify

wallet_router = Blueprint(
    "wallet",
    __name__
)


@wallet_router.post("/api/wallet/fund")
def fund_wallet():

    data = request.json

    telegram_id = data.get("telegram_id")
    amount = data.get("amount")

    if amount < 1500:

        return jsonify({
            "error": "Minimum funding is ₦1,500"
        }), 400

    return jsonify({
        "message": "Payment initialized"
    })