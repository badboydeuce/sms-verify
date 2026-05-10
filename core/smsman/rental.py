# core/smsman/rental.py

import httpx
import os

BASE_URL = "https://api.sms-man.com/rent-api"

TOKEN = os.getenv("SMSMAN_TOKEN")


class SMSManRental:

    @staticmethod
    async def get_limits(country_id, rent_type, time):
        params = {
            "token": TOKEN,
            "type": rent_type,
            "time": str(time)
        }

        # ✅ Only add country_id if provided
        if country_id:
            params["country_id"] = str(country_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/limits",
                params=params
            )
            print(f"RENTAL LIMITS: {response.status_code} {response.text}", flush=True)
            return response.json()

    @staticmethod
    async def get_number(country_id, rent_type, time):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/get-number",
                params={
                    "token": TOKEN,
                    "country_id": str(country_id),
                    "type": rent_type,
                    "time": str(time)
                }
            )
            print(f"RENTAL GET-NUMBER: {response.status_code} {response.text}", flush=True)
            return response.json()

    @staticmethod
    async def get_sms(request_id):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/get-sms",
                params={
                    "token": TOKEN,
                    "request_id": str(request_id)
                }
            )
            return response.json()

    @staticmethod
    async def get_all_sms(request_id):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/get-all-sms",
                params={
                    "token": TOKEN,
                    "request_id": str(request_id)
                }
            )
            return response.json()
