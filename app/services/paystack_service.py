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

    # =========================
    # 💰 INIT PAYMENT
    # =========================
    def initialize_transaction(self, email, amount, user_id):
        url = f"{self.BASE_URL}/transaction/initialize"

        payload = {
            "email": email,
            "amount": amount,
            "currency": "NGN",
            "metadata": {"user_id": user_id},
            "callback_url": settings.PAYSTACK_CALLBACK_URL
        }

        try:
            res = requests.post(url, json=payload, headers=self.headers, timeout=15)
            data = res.json()

            if data.get("status"):
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "reference": data["data"]["reference"]
                }

            return {"success": False, "error": data.get("message")}

        except Exception as e:
            logger.error(e)
            return {"success": False, "error": str(e)}

    # =========================
    # 🔍 VERIFY
    # =========================
    def verify_transaction(self, reference):
        url = f"{self.BASE_URL}/transaction/verify/{reference}"

        try:
            res = requests.get(url, headers=self.headers, timeout=15)
            data = res.json()

            if data.get("status") and data["data"]["status"] == "success":
                return {
                    "success": True,
                    "amount": data["data"]["amount"] / 100
                }

            return {"success": False}

        except Exception as e:
            logger.error(e)
            return {"success": False}
