import requests
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class PaystackService:
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def initialize_transaction(self, email: str, amount: int, user_id: int, metadata=None):
        """Create payment session"""
        url = f"{self.BASE_URL}/transaction/initialize"

        payload = {
            "email": email,
            "amount": amount,  # in kobo
            "currency": "NGN",
            "metadata": {
                "user_id": user_id,
                **(metadata or {})
            },
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            data = response.json()

            if data.get("status") is True:
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "reference": data["data"]["reference"],
                    "amount": amount / 100
                }
            else:
                logger.error(f"Paystack error: {data.get('message')}")
                return {"success": False, "error": data.get("message")}

        except Exception as e:
            logger.error(f"Paystack request failed: {e}")
            return {"success": False, "error": str(e)}

    def save_payment_record(self, reference: str, user_id: int):
        """Save reference for later verification"""
        try:
            from app.webhook.paystack_webhook import payment_records
            payment_records[reference] = user_id
            logger.info(f"Saved payment record: {reference} -> user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save payment record: {e}")


# Singleton instance
paystack = PaystackService()
