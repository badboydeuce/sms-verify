import requests
import os
import time

SMS_API_KEY = os.getenv("SMS_API_KEY")

_cache = {
    "countries": {"data": None, "time": 0},
    "services": {}
}

CACHE_TTL = 300  # 5 minutes

BASE_URL = "https://api.sms-man.com/stubs/handler_api.php"


def get_countries():
    now = time.time()

    if _cache["countries"]["data"] and now - _cache["countries"]["time"] < CACHE_TTL:
        return _cache["countries"]["data"]

    res = requests.get(BASE_URL, params={
        "api_key": SMS_API_KEY,
        "action": "getCountries"
    })

    data = res.json()

    _cache["countries"] = {
        "data": data,
        "time": now
    }

    return data


def get_services(country_id: int):
    now = time.time()

    if country_id in _cache["services"]:
        cached = _cache["services"][country_id]
        if now - cached["time"] < CACHE_TTL:
            return cached["data"]

    res = requests.get(BASE_URL, params={
        "api_key": SMS_API_KEY,
        "action": "getServices",
        "country": country_id
    })

    data = res.json()

    _cache["services"][country_id] = {
        "data": data,
        "time": now
    }

    return data