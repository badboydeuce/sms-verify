# app/webhook/paystack_webhook.py
from flask import Flask, request
import requests
import logging
import os
from app.config import settings

app = Flask(__name__)
logger = logging.getLogger(__name__)

payment_records = {}  # Temporary storage (replace with DB later)

@app.route('/paystack/verify', methods=['GET'])
def paystack_callback():
    reference = request.args.get('reference')
    
    if not reference:
        return "<h2>❌ Invalid Request</h2>", 400

    result = verify_transaction(reference)
    
    if result['success']:
        user_id = payment_records.get(reference)
        amount = result['amount']
        
        if user_id:
            credit_wallet(user_id, amount, reference)
            notify_user_on_telegram(user_id, amount)
            
            return f"""
            <h2>✅ Payment Successful!</h2>
            <p><strong>Amount:</strong> ₦{amount:,.0f}</p>
            <p><strong>Reference:</strong> {reference}</p>
            <p>Your wallet has been credited successfully.</p>
            <hr>
            <p>Thank you for using DeuceVerify!</p>
            """, 200
        else:
            return "<h2>✅ Payment Verified but user mapping not found.</h2>", 200
    else:
        return "<h2>❌ Payment verification failed.</h2>", 400


def verify_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        
        if data.get("status") and data["data"]["status"] == "success":
            return {
                "success": True,
                "amount": data["data"]["amount"] / 100
            }
    except Exception as e:
        logger.error(f"Verification failed: {e}")
    
    return {"success": False}


def credit_wallet(user_id, amount, reference):
    print(f"💰 Crediting user {user_id} ₦{amount} | Ref: {reference}")
    # TODO: Add real wallet logic here later


def notify_user_on_telegram(user_id, amount):
    try:
        from telegram import Bot
        bot = Bot(token=settings.BOT_TOKEN)
        bot.send_message(
            chat_id=user_id,
            text=f"✅ **Payment Successful!**\n\n"
                 f"₦{amount:,.0f} has been added to your balance.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Telegram notify failed: {e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
