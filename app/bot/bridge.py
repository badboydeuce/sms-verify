# app/bot/bridge.py

import requests

API_BASE = "http://localhost:5000"


# =========================
# 🌍 COUNTRIES
# =========================
def get_countries():
    res = requests.get(f"{API_BASE}/numbers/countries")
    return res.json()


# =========================
# 📱 SERVICES
# =========================
def get_services(country_id):
    res = requests.get(f"{API_BASE}/numbers/services", params={
        "country_id": country_id
    })
    return res.json()


# =========================
# 📞 BUY NUMBER
# =========================
def buy_number(country, service, user_id):
    res = requests.post(f"{API_BASE}/numbers/buy", json={
        "country": country,
        "service": service,
        "user_id": user_id
    })
    return res.json()


# =========================
# 📩 CHECK OTP
# =========================
def check_otp(request_id):
    res = requests.get(f"{API_BASE}/otp/check/{request_id}")
    return res.json()


# =========================
# 💰 WALLET
# =========================
def get_balance(user_id):
    res = requests.get(f"{API_BASE}/wallet/balance/{user_id}")
    return res.json()
