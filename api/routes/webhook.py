from flask import Blueprint, request, jsonify

webhook_router = Blueprint(
    "webhook",
    __name__
)


@webhook_router.post("/api/webhook/paystack")
def paystack_webhook():

    signature = request.headers.get(
        "x-paystack-signature"
    )

    payload = request.data

    # verify signature here

    return jsonify({
        "status": "success"
    })