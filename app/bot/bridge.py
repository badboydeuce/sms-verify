# app/bot/bridge.py

import os
import httpx

API_BASE = os.getenv("API_URL")


async def get_countries():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/numbers/countries")
        return res.json()


async def get_services(country_id):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{API_BASE}/numbers/services",
            params={"country_id": country_id}
        )
        return res.json()


async def buy_number(country, service, user_id):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{API_BASE}/numbers/buy",
            json={
                "country": country,
                "service": service,
                "user_id": user_id
            }
        )
        return res.json()


async def check_otp(request_id):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/otp/check/{request_id}")
        return res.json()


async def get_balance(user_id):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE}/wallet/balance/{user_id}")
        return res.json()


async def init_payment(user_id, amount, email):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{API_BASE}/wallet/fund",
            json={
                "user_id": user_id,
                "amount": amount,
                "email": email
            }
        )
        return res.json()
