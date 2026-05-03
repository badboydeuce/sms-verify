# app/services/paystack_service.py

import requests
import logging
from app.config import settings
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

wallet = WalletService()


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

        url = f"{self.BASE_URL}/transaction/initialize"

        payload = {
            "email": email,
            "amount": int(amount * 100),  # kobo
            "currency": "NGN",
            "metadata": {
                "telegram_id": str(telegram_id),
                "purpose": "wallet_funding"
            },
            "callback_url": settings.PAYSTACK_CALLBACK_URL
        }

        try:
            logger.info(f"Init payment: {email} | TG: {telegram_id}")

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

            return {
                "success": False,
                "error": data.get("message", "Init failed")
            }

        except Exception as e:
            logger.exception("Paystack init error")
            return {"success": False, "error": str(e)}

    # =========================
    # 🔍 VERIFY TRANSACTION
    # =========================
    def verify_transaction(self, reference):

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
                    "amount": data["data"]["amount"] / 100,
                    "email": data["data"]["customer"]["email"],
                    "reference": reference,
                    "telegram_id": data["data"]["metadata"].get("telegram_id")
                }

            return {
                "success": False,
                "error": "Transaction not successful"
            }

        except Exception as e:
            logger.exception("Paystack verify error")
            return {"success": False, "error": str(e)}

    # =========================
    # 💰 CREDIT WALLET (IMPORTANT)
    # =========================
    def credit_wallet(self, telegram_id: str, amount: float, reference: str):
        """
        Safe wallet credit with duplicate protection
        """

        try:
            # prevent double credit (IMPORTANT)
            conn = wallet.get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT 1 FROM transactions WHERE reference=?",
                (reference,)
            )

            if cur.fetchone():
                logger.warning("Duplicate Paystack credit blocked")
                return False

            conn.close()

            # credit wallet
            return wallet.add_balance(
                user_id=telegram_id,
                amount=amount,
                reference=reference
            )

        except Exception as e:
            logger.exception("Wallet credit error")
            return False