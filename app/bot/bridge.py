# app/bot/bridge.py

import os
import httpx

API_BASE = os.getenv("API_URL")

print("🌐 API BASE:", API_BASE)


# =========================
# 🌍 GET COUNTRIES
# =========================
async def get_countries():
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(f"{API_BASE}/numbers/countries")

            print("🌍 COUNTRIES STATUS:", res.status_code)
            print("🌍 COUNTRIES RESPONSE:", res.text)

            if res.status_code != 200:
                return {"success": False}

            return res.json()

    except Exception as e:
        print("❌ COUNTRIES ERROR:", str(e))
        return {"success": False}


# =========================
# 📦 GET SERVICES
# =========================
async def get_services(country_id):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(
                f"{API_BASE}/numbers/services",
                params={"country_id": country_id}
            )

            print("📦 SERVICES STATUS:", res.status_code)
            print("📦 SERVICES RESPONSE:", res.text)

            if res.status_code != 200:
                return {"success": False}

            return res.json()

    except Exception as e:
        print("❌ SERVICES ERROR:", str(e))
        return {"success": False}


# =========================
# 📱 BUY NUMBER
# =========================
async def buy_number(country, service, user_id):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(
                f"{API_BASE}/numbers/buy",
                json={
                    "country": country,
                    "service": service,
                    "user_id": user_id
                }
            )

            print("📱 BUY STATUS:", res.status_code)
            print("📱 BUY RESPONSE:", res.text)

            if res.status_code != 200:
                return {"success": False}

            return res.json()

    except Exception as e:
        print("❌ BUY ERROR:", str(e))
        return {"success": False}


# =========================
# 🔐 CHECK OTP
# =========================
async def check_otp(request_id):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(f"{API_BASE}/otp/check/{request_id}")

            print("🔐 OTP STATUS:", res.status_code)
            print("🔐 OTP RESPONSE:", res.text)

            if res.status_code != 200:
                return {"success": False}

            return res.json()

    except Exception as e:
        print("❌ OTP ERROR:", str(e))
        return {"success": False}


# =========================
# 💰 GET BALANCE
# =========================
async def get_balance(user_id):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(f"{API_BASE}/wallet/balance/{user_id}")

            print("💰 BALANCE STATUS:", res.status_code)
            print("💰 BALANCE RESPONSE:", res.text)

            if res.status_code != 200:
                return {"success": False, "balance": 0}

            return res.json()

    except Exception as e:
        print("❌ BALANCE ERROR:", str(e))
        return {"success": False, "balance": 0}


# =========================
# 💳 INIT PAYMENT
# =========================
async def init_payment(user_id, amount, email):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(
                f"{API_BASE}/wallet/fund",
                json={
                    "user_id": user_id,
                    "amount": amount,
                    "email": email
                }
            )

            print("💳 PAYMENT STATUS:", res.status_code)
            print("💳 PAYMENT RESPONSE:", res.text)

            if res.status_code != 200:
                return {"success": False}

            return res.json()

    except Exception as e:
        print("❌ PAYMENT ERROR:", str(e))
        return {"success": False}
