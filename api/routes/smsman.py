# api/routes/smsman.py

from fastapi import APIRouter, HTTPException
import httpx
import os
import time

router = APIRouter()

SMSMAN_TOKEN = os.getenv("SMSMAN_TOKEN")
BASE_URL = "https://api.sms-man.com/control"

# Cache
_prices_cache = {}
_cache_ttl = 300  # 5 minutes


@router.get("/api/smsman/prices/{country_id}")
async def get_prices(country_id: str):
    cache_key = country_id
    now = time.time()

    # Return cached if fresh
    if cache_key in _prices_cache:
        cached_at, cached_data = _prices_cache[cache_key]
        if now - cached_at < _cache_ttl:
            return cached_data

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            http2=False
        ) as client:
            response = await client.get(
                f"{BASE_URL}/get-prices",
                params={
                    "token": SMSMAN_TOKEN,
                    "country_id": country_id
                }
            )
            response.raise_for_status()
            data = response.json()

        # Store in cache
        _prices_cache[cache_key] = (now, data)

        return data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SMS-Man API error: {str(e)}"
        )


@router.get("/api/smsman/countries")
async def get_countries():
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            http2=False
        ) as client:
            response = await client.get(
                f"{BASE_URL}/countries",
                params={"token": SMSMAN_TOKEN}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"SMS-Man API error: {str(e)}"
        )
