# core/smsman/activation.py

import asyncio
import httpx
import os

BASE_URL = "https://api.sms-man.com/control"

MAX_RETRIES = 3
RETRY_DELAY = 1


class SMSManActivation:

    @staticmethod
    def _token() -> str:
        token = os.getenv("SMSMAN_TOKEN")
        if not token:
            raise ValueError("SMSMAN_TOKEN environment variable is not set")
        return token

    @staticmethod
    async def _get(url: str, params: dict) -> dict:
        """Shared GET with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
            except (httpx.ReadError, httpx.RemoteProtocolError, httpx.ConnectError) as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(RETRY_DELAY)
        return {}

    @staticmethod
    async def get_balance():
        return await SMSManActivation._get(
            f"{BASE_URL}/get-balance",
            {"token": SMSManActivation._token()}
        )

    @staticmethod
    async def get_countries():
        return await SMSManActivation._get(
            f"{BASE_URL}/countries",
            {"token": SMSManActivation._token()}
        )

    @staticmethod
    async def get_services():
        return await SMSManActivation._get(
            f"{BASE_URL}/applications",
            {"token": SMSManActivation._token()}
        )

    @staticmethod
    async def get_prices(country_id: int):
        return await SMSManActivation._get(
            f"{BASE_URL}/get-prices",
            {
                "token": SMSManActivation._token(),
                "country_id": country_id
            }
        )

    @staticmethod
    async def get_number(country_id: int, application_id: int):
        return await SMSManActivation._get(
            f"{BASE_URL}/get-number",
            {
                "token": SMSManActivation._token(),
                "country_id": country_id,
                "application_id": application_id
            }
        )

    @staticmethod
    async def get_sms(request_id: int):
        return await SMSManActivation._get(
            f"{BASE_URL}/get-sms",
            {
                "token": SMSManActivation._token(),
                "request_id": request_id
            }
        )

    @staticmethod
    async def set_status(request_id: int, status: str):
        valid_statuses = {"ready", "close", "reject", "used"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}")
        return await SMSManActivation._get(
            f"{BASE_URL}/set-status",
            {
                "token": SMSManActivation._token(),
                "request_id": request_id,
                "status": status
            }
        )
