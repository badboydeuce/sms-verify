import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

class Settings:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.SMSMAN_API_KEY = os.getenv("SMSMAN_API_KEY")

settings = Settings()
