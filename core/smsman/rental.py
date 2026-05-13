# core/smsman/rental.py

import httpx
import os

BASE_URL = "https://api.sms-man.com/rent-api"
TOKEN = os.getenv("SMSMAN_TOKEN")


class SMSManRental:

    @staticmethod
    async def get_limits(rent_type: str, time: int, country_id: str = None) -> dict:
        params = {
            "token": TOKEN,
            "type": rent_type,
            "time": str(time)
        }
        if country_id:
            params["country_id"] = str(country_id)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{BASE_URL}/limits", params=params)
            response.raise_for_status()
            data = response.json()
            print(f"RENTAL LIMITS: {data}", flush=True)
            return data

    @staticmethod
    async def get_number(country_id: str, rent_type: str, time: int) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-number",
                params={
                    "token": TOKEN,
                    "country_id": str(country_id),
                    "type": rent_type,
                    "time": str(time)
                }
            )
            response.raise_for_status()
            data = response.json()
            print(f"RENTAL GET-NUMBER: {data}", flush=True)
            return data

    @staticmethod
    async def get_sms(request_id: int) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-sms",
                params={"token": TOKEN, "request_id": str(request_id)}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_all_sms(request_id: int) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-all-sms",
                params={"token": TOKEN, "request_id": str(request_id)}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def set_status(request_id: int, status: str) -> dict:
        valid = {"cancel", "close"}
        if status not in valid:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid}")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/set-status",
                params={
                    "token": TOKEN,
                    "request_id": str(request_id),
                    "status": status
                }
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_all_requests() -> list:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-all-requests",
                params={"token": TOKEN}
            )
            response.raise_for_status()
            return response.json()
