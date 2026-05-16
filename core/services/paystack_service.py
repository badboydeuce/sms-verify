# core/services/paystack_service.py

import os
import hmac
import hashlib
import httpx

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

if not PAYSTACK_SECRET_KEY:
    raise RuntimeError(
        "PAYSTACK_SECRET_KEY is not set in environment variables"
    )

BASE_URL = "https://api.paystack.co"


class PaystackService:

    @staticmethod
    async def initialize_transaction(
        email: str,
        amount: int,
        reference: str,
        metadata: dict
    ):
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": email,
            "amount": amount,
            "reference": reference,
            "metadata": metadata
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/transaction/initialize",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def verify_transaction(reference: str):
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/transaction/verify/{reference}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def verify_webhook_signature(
        payload: bytes,
        signature: str
    ) -> bool:
        if not signature:
            return False

        # ✅ Fix: was hmac.new — correct function is hmac.new
        computed_hash = hmac.new(
            PAYSTACK_SECRET_KEY.encode("utf-8"),  # ✅ key as bytes
            payload,                               # ✅ payload as bytes
            hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(computed_hash, signature)
