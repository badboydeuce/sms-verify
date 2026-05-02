from flask import Flask, request, jsonify
import requests
import logging
from app.config import settings
from app.services.paystack_service import paystack

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Store user reference mapping temporarily (use database in production)
payment_records = {}   # reference -> user_id


@app.route('/paystack/verify', methods=['GET'])
def paystack_callback():
    reference = request.args.get('reference')
    
    if not reference:
        return "Invalid request", 400

    # Verify transaction with Paystack
    result = verify_paystack_transaction(reference)
    
    if result['success']:
        user_id = payment_records.get(reference)
        
        if user_id:
            amount = result['amount']
            # TODO: Credit user's wallet here
            credit_user_wallet(user_id, amount, reference)
            
            # Notify user on Telegram
            notify_user_on_telegram(user_id, amount)
            
            return f"""
            <h2>✅ Payment Successful!</h2>
            <p>Amount: ₦{amount:,.0f}</p>
            <p>Reference: {reference}</p>
            <p>Your wallet has been credited.</p>
            """, 200
        else:
            return "Payment verified but user not found.", 200
    else:
        return f"Payment verification failed: {result.get('error')}", 400


def verify_paystack_transaction(reference: str):
    """Verify transaction with Paystack"""
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data.get("status") and data["data"]["status"] == "success":
            return {
                "success": True,
                "amount": data["data"]["amount"] / 100,  # Convert from kobo
                "reference": reference
            }
        else:
            return {"success": False, "error": "Transaction not successful"}
            
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return {"success": False, "error": str(e)}


def credit_user_wallet(user_id: int, amount: float, reference: str):
    """TODO: Implement wallet credit logic"""
    print(f"💰 Crediting user {user_id} with ₦{amount} | Ref: {reference}")
    # Add to database here later


def notify_user_on_telegram(user_id: int, amount: float):
    """Send success message to user via Telegram Bot"""
    from telegram import Bot
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        bot.send_message(
            chat_id=user_id,
            text=f"✅ **Payment Successful!**\n\n"
                 f"₦{amount:,.0f} has been added to your wallet.\n"
                 f"You can now buy numbers."
        )
    except:
        pass  # User might have blocked bot


if __name__ == '__main__':
    app.run(port=5000, debug=True)
