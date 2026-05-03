# app/services/paystack_service.py

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
    # 💰 INITIALIZE TRANSACTION
    # =========================
    def initialize_transaction(self, email, amount, telegram_id):
        """
        Creates Paystack payment link with metadata for wallet crediting
        """

        url = f"{self.BASE_URL}/transaction/initialize"

        payload = {
            "email": email,

            # Paystack expects amount in kobo
            "amount": int(amount * 100),

            "currency": "NGN",

            # 🔥 IMPORTANT: used for wallet mapping in webhook
            "metadata": {
                "telegram_id": str(telegram_id),
                "purpose": "wallet_funding"
            },

            # optional redirect after payment
            "callback_url": settings.PAYSTACK_CALLBACK_URL
        }

        try:
            logger.info(f"Initializing Paystack payment for {email} (TG: {telegram_id})")

            res = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=15
            )

            data = res.json()

            if data.get("status") and data.get("data"):
                return {
                    "success": True,
                    "authorization_url": data["data"]["authorization_url"],
                    "reference": data["data"]["reference"]
                }

            logger.error(f"Paystack init failed: {data}")
            return {
                "success": False,
                "error": data.get("message", "Payment initialization failed")
            }

        except Exception as e:
            logger.exception("Paystack initialization error")
            return {
                "success": False,
                "error": str(e)
            }

    # =========================
    # 🔍 VERIFY TRANSACTION
    # =========================
    def verify_transaction(self, reference):
        """
        Verifies Paystack transaction using reference
        """

        url = f"{self.BASE_URL}/transaction/verify/{reference}"

        try:
            res = requests.get(
                url,
                headers=self.headers,
                timeout=15
            )

            data = res.json()

            if (
                data.get("status")
                and data.get("data")
                and data["data"].get("status") == "success"
            ):
                return {
                    "success": True,
                    "amount": data["data"]["amount"] / 100,  # convert kobo → NGN
                    "email": data["data"]["customer"]["email"],
                    "reference": reference
                }

            logger.warning(f"Verification failed: {data}")
            return {
                "success": False,
                "error": "Transaction not successful"
            }

        except Exception as e:
            logger.exception("Paystack verification error")
            return {
                "success": False,
                "error": str(e)
            }