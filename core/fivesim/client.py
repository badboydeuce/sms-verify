# core/fivesim/client.py

import httpx
import os

BASE_URL = "https://5sim.net/v1"
TOKEN = os.getenv("FIVESIM_TOKEN")


def _headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    }


class FiveSimClient:

    # ===================== COUNTRIES =====================
    @staticmethod
    async def get_countries() -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/guest/countries",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    # ===================== PRODUCTS & PRICES =====================
    @staticmethod
    async def get_products(country: str, operator: str = "any") -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/guest/products/{country}/{operator}",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_prices_by_country(country: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/guest/prices",
                headers={"Accept": "application/json"},
                params={"country": country}
            )
            response.raise_for_status()
            return response.json()

    # ===================== PURCHASE =====================
    @staticmethod
    async def buy_activation(
        country: str,
        product: str,
        operator: str = "any"
    ) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/user/buy/activation/{country}/{operator}/{product}",
                headers=_headers()
            )
            response.raise_for_status()
            return response.json()

    # ===================== ORDER MANAGEMENT =====================
    @staticmethod
    async def check_order(order_id: int) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/user/check/{order_id}",
                headers=_headers()
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def finish_order(order_id: int) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/user/finish/{order_id}",
                headers=_headers()
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def cancel_order(order_id: int) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/user/cancel/{order_id}",
                headers=_headers()
            )
            response.raise_for_status()
            return response.json()

    # ===================== BALANCE =====================
    @staticmethod
    async def get_balance() -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{BASE_URL}/user/profile",
                headers=_headers()
            )
            response.raise_for_status()
            return response.json()
