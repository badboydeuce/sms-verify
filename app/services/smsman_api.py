# app/services/smsman_api.py

import requests
import os
import time
import logging

logger = logging.getLogger(__name__)

SMS_API_KEY = os.getenv("SMS_API_KEY")

BASE_URL = "https://api.sms-man.com/stubs/handler_api.php"

CACHE_TTL = 300  # 5 minutes

_cache = {
    "countries": {"data": None, "time": 0},
    "services": {}
}


# =========================
# 🌍 COUNTRIES
# =========================
def get_countries():
    now = time.time()

    # return cache if valid
    if _cache["countries"]["data"] and now - _cache["countries"]["time"] < CACHE_TTL:
        return _cache["countries"]["data"]

    try:
        res = requests.get(
            BASE_URL,
            params={
                "api_key": SMS_API_KEY,
                "action": "getCountries"
            },
            timeout=10
        )

        data = res.json()

        _cache["countries"] = {
            "data": data,
            "time": now
        }

        return data

    except Exception as e:
        logger.exception("Failed to fetch countries")
        return []


# =========================
# 📱 SERVICES
# =========================
def get_services(country_id: int):
    now = time.time()

    # cache check
    if country_id in _cache["services"]:
        cached = _cache["services"][country_id]

        if now - cached["time"] < CACHE_TTL:
            return cached["data"]

    try:
        res = requests.get(
            BASE_URL,
            params={
                "api_key": SMS_API_KEY,
                "action": "getServices",
                "country": country_id
            },
            timeout=10
        )

        data = res.json()

        _cache["services"][country_id] = {
            "data": data,
            "time": now
        }

        return data

    except Exception as e:
        logger.exception("Failed to fetch services")
        return []