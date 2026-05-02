import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()


class Settings:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.SMSMAN_API_KEY = os.getenv("SMSMAN_API_KEY")
        
        # =====================
        # Paystack Configuration
        # =====================
        self.PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
        self.PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")   # Optional but useful
        self.PAYSTACK_CALLBACK_URL = os.getenv(
            "PAYSTACK_CALLBACK_URL", 
            "https://yourdomain.com/paystack/verify"  # Change later if needed
        )

        # Optional: Default amounts in Kobo
        self.PAYSTACK_DEFAULT_AMOUNTS = {
            "1000": 100000,   # ₦1,000
            "2000": 200000,   # ₦2,000
            "5000": 500000,   # ₦5,000
            "10000": 1000000, # ₦10,000
            "20000": 2000000, # ₦20,000
        }


settings = Settings()
