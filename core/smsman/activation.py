import httpx
import os

BASE_URL = "https://api.sms-man.com/control"

TOKEN = os.getenv("SMSMAN_TOKEN")


class SMSManActivation:

    @staticmethod
    async def get_balance():

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{BASE_URL}/get-balance",
                params={
                    "token": TOKEN
                }
            )

            return response.json()

    @staticmethod
    async def get_countries():

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{BASE_URL}/countries",
                params={
                    "token": TOKEN
                }
            )

            return response.json()

    @staticmethod
    async def get_services():

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{BASE_URL}/applications",
                params={
                    "token": TOKEN
                }
            )

            return response.json()

    @staticmethod
    async def get_prices(country_id):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{BASE_URL}/get-prices",
                params={
                    "token": TOKEN,
                    "country_id": country_id
                }
            )

            return response.json()

    @staticmethod
    async def get_number(country_id, application_id):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{BASE_URL}/get-number",
                params={
                    "token": TOKEN,
                    "country_id": country_id,
                    "application_id": application_id
                }
            )

            return response.json()

    @staticmethod
    async def get_sms(request_id):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{BASE_URL}/get-sms",
                params={
                    "token": TOKEN,
                    "request_id": request_id
                }
            )

            return response.json()