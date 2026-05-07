import httpx
import os

BASE_URL = "https://api.sms-man.com/stubs/handler_api.php"

TOKEN = os.getenv("SMSMAN_TOKEN")


class SMSManCompatible:

    @staticmethod
    async def get_balance():

        async with httpx.AsyncClient() as client:

            response = await client.get(
                BASE_URL,
                params={
                    "api_key": TOKEN,
                    "action": "getBalance"
                }
            )

            return response.text