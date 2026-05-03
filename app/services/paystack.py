# app/services/paystack.py

import requests
from app.core.config import settings


class PaystackService:

    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret = settings.PAYSTACK_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret}",
            "Content-Type": "application/json"
        }

    # =========================
    # 💰 INIT PAYMENT
    # =========================
    def initialize(self, email, amount, user_id):

        payload = {
            "email": email,
            "amount": int(amount * 100),
            "metadata": {"telegram_id": user_id}
        }

        res = requests.post(
            f"{self.BASE_URL}/transaction/initialize",
            json=payload,
            headers=self.headers
        )

        return res.json()

    # =========================
    # 🔍 VERIFY PAYMENT
    # =========================
    def verify(self, reference):

        res = requests.get(
            f"{self.BASE_URL}/transaction/verify/{reference}",
            headers=self.headers
        )

        return res.json()
