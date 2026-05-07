from flask import Blueprint, jsonify

orders_router = Blueprint(
    "orders",
    __name__
)


@orders_router.get("/api/order/otp/<order_id>")
def get_otp(order_id):

    return jsonify({
        "otp": None
    })


@orders_router.post("/api/order/cancel/<order_id>")
def cancel_order(order_id):

    return jsonify({
        "status": "cancelled"
    })