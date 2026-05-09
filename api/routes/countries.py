# api/routes/countries.py

from fastapi import APIRouter
import httpx
import os

router = APIRouter()

SMSMAN_TOKEN = os.getenv("SMSMAN_TOKEN")


@router.get("/countries")
async def get_countries():

    url = "https://api.sms-man.com/control/get-countries"

    params = {
        "token": SMSMAN_TOKEN
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    return response.json()