from dotenv import load_dotenv
import os

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if DATABASE_URL:

    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://"
    )

SMSMAN_TOKEN = os.getenv(
    "SMSMAN_TOKEN"
)

PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY"
)

API_BASE_URL = os.getenv(
    "API_BASE_URL"
)

ADMIN_IDS = [
    int(x)
    for x in os.getenv(
        "ADMIN_IDS",
        ""
    ).split(",")

    if x
]