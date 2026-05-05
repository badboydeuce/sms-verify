import requests
from requests.exceptions import RequestException
from app.core.config import settings


class PaystackService:

    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret = settings.PAYSTACK_SECRET_KEY

        if not self.secret:
            raise ValueError("PAYSTACK_SECRET_KEY not set")

        self.headers = {
            "Authorization": f"Bearer {self.secret}",
            "Content-Type": "application/json"
        }

    # =========================
    # 💰 INIT PAYMENT
    # =========================
    def initialize(self, email: str, amount: float, user_id: str):

        try:
            payload = {
                "email": email,
                "amount": int(amount * 100),
                "metadata": {
                    "telegram_id": user_id
                }
            }

            res = requests.post(
                f"{self.BASE_URL}/transaction/initialize",
                json=payload,
                headers=self.headers,
                timeout=10
            )

            data = res.json()

            if not data.get("status"):
                return {
                    "success": False,
                    "message": data.get("message", "Initialization failed")
                }

            return {
                "success": True,
                "authorization_url": data["data"]["authorization_url"],
                "reference": data["data"]["reference"]
            }

        except RequestException as e:
            return {
                "success": False,
                "message": str(e)
            }

    # =========================
    # 🔍 VERIFY PAYMENT
    # =========================
    def verify(self, reference: str):

        try:
            res = requests.get(
                f"{self.BASE_URL}/transaction/verify/{reference}",
                headers=self.headers,
                timeout=10
            )

            data = res.json()

            if not data.get("status"):
                return {
                    "success": False,
                    "message": data.get("message", "Verification failed")
                }

            payment_data = data["data"]

            return {
                "success": payment_data["status"] == "success",
                "amount": payment_data["amount"] / 100,
                "reference": payment_data["reference"],
                "email": payment_data["customer"]["email"]
            }

        except RequestException as e:
            return {
                "success": False,
                "message": str(e)
            }