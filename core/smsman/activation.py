import httpx
import os

BASE_URL = "https://api.sms-man.com/control"


class SMSManActivation:

    @staticmethod
    def _token() -> str:
        token = os.getenv("SMSMAN_TOKEN")
        if not token:
            raise ValueError("SMSMAN_TOKEN environment variable is not set")
        return token

    @staticmethod
    async def get_balance():
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-balance",
                params={"token": SMSManActivation._token()}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_countries():
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/countries",
                params={"token": SMSManActivation._token()}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_services():
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/applications",
                params={"token": SMSManActivation._token()}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_prices(country_id: int):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-prices",
                params={"token": SMSManActivation._token(), "country_id": country_id}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_number(country_id: int, application_id: int):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-number",
                params={
                    "token": SMSManActivation._token(),
                    "country_id": country_id,
                    "application_id": application_id
                }
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_sms(request_id: int):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/get-sms",
                params={"token": SMSManActivation._token(), "request_id": request_id}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def set_status(request_id: int, status: str):
        valid_statuses = {"ready", "close", "reject", "used"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/set-status",
                params={
                    "token": SMSManActivation._token(),
                    "request_id": request_id,
                    "status": status
                }
            )
            response.raise_for_status()
            return response.json()
