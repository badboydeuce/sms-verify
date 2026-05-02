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
        """
        amount: in Kobo (e.g. 5000 = ₦50)
        """
        url = f"{self.BASE_URL}/transaction/initialize"

        payload = {
            "email": email,
            "amount": amount,           # in kobo
            "currency": "NGN",
            "metadata": {
                "user_id": user_id,
                **(metadata or {})
            },
            "callback_url": settings.PAYSTACK_CALLBACK_URL,  # e.g. https://yourdomain.com/verify
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            data = response.json()

            if data.get("status") is True:
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "reference": data["data"]["reference"],
                    "amount": amount / 100  # back to Naira
                }
            else:
                logger.error(f"Paystack error: {data}")
                return {"success": False, "error": data.get("message")}

        except Exception as e:
            logger.error(f"Paystack request failed: {e}")
            return {"success": False, "error": str(e)}


# Singleton
paystack = PaystackService()
