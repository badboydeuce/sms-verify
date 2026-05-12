# api/routes/smsman.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import time
import json

router = APIRouter()

SMSMAN_TOKEN = os.getenv("SMSMAN_TOKEN")
BASE_URL = "https://api.sms-man.com/control"

_prices_cache = {}
_cache_ttl = 60


@router.get("/api/smsman/prices/{country_id}")
async def get_prices(country_id: str):
    cache_key = country_id
    now = time.time()

    if cache_key in _prices_cache:
        cached_at, cached_data = _prices_cache[cache_key]
        if now - cached_at < _cache_ttl:
            return JSONResponse(content=cached_data)

    url = f"{BASE_URL}/get-prices"
    params = {"token": SMSMAN_TOKEN, "country_id": country_id}

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=15.0),
                http2=False,
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10
                )
            ) as client:
                async with client.stream("GET", url, params=params) as response:
                    response.raise_for_status()
                    chunks = []
                    async for chunk in response.aiter_bytes():
                        chunks.append(chunk)
                    raw = b"".join(chunks)
                    data = json.loads(raw)

            # ✅ Debug — log first item structure
            first_key = next(iter(data), None)
            if first_key:
                print(f"SMS-MAN RAW FIRST KEY: {first_key}", flush=True)
                print(f"SMS-MAN RAW FIRST VALUE: {data[first_key]}", flush=True)

            _prices_cache[cache_key] = (now, data)
            return JSONResponse(content=data)

        except Exception as e:
            if attempt == 2:
                raise HTTPException(
                    status_code=500,
                    detail=f"SMS-Man API error: {str(e)}"
                )
            import asyncio
            await asyncio.sleep(2 * (attempt + 1))



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
