# app/core/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Central configuration for DeuceVerify system.
    """

    def __init__(self):
        # =========================
        # BOT CONFIG
        # =========================
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")

        # =========================
        # SMS-MAN CONFIG
        # =========================
        self.SMSMAN_API_KEY = os.getenv("SMSMAN_API_KEY")

        # =========================
        # PAYSTACK CONFIG
        # =========================
        self.PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
        self.PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
        self.PAYSTACK_CALLBACK_URL = os.getenv(
            "PAYSTACK_CALLBACK_URL",
            "https://yourdomain.com/webhook/paystack"
        )

        # =========================
        # DATABASE
        # =========================
        self.DATABASE_URL = os.getenv("DATABASE_URL")

        # =========================
        # SYSTEM SETTINGS
        # =========================
        self.CURRENCY = "NGN"
        self.OTP_EXPIRY_SECONDS = 300
        self.REQUEST_TIMEOUT = 15


settings = Settings()
