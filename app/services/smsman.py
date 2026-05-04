# app/services/smsman.py

import requests
from app.core.config import settings


class SMSManProvider:
    BASE_URL = "https://api.sms-man.com/control/"

    def __init__(self):
        self.token = settings.SMSMAN_API_KEY

    # =========================
    # 💰 BALANCE (optional but useful)
    # =========================
    def get_balance(self):
        try:
            res = requests.get(
                self.BASE_URL + "get-balance",
                params={"token": self.token},
                timeout=10
            )
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    # =========================
    # 📞 BUY NUMBER (FIXED)
    # =========================
    def get_number(self, country_id: str, application_id: str):

        try:
            res = requests.get(
                self.BASE_URL + "get-number",
                params={
                    "token": self.token,
                    "country_id": country_id,
                    "application_id": application_id
                },
                timeout=10
            )

            data = res.json()

            # ❌ API error
            if "success" in data and data.get("success") is False:
                return {"error": data.get("error_msg")}

            return {
                "request_id": data["request_id"],
                "number": data["number"],
                "country_id": data["country_id"],
                "application_id": data["application_id"]
            }

        except Exception as e:
            return {"error": str(e)}

    # =========================
    # 📩 GET SMS (FIXED)
    # =========================
    def get_sms(self, request_id: str):

        try:
            res = requests.get(
                self.BASE_URL + "get-sms",
                params={
                    "token": self.token,
                    "request_id": request_id
                },
                timeout=10
            )

            data = res.json()

            # ⏳ still waiting
            if data.get("error_code") == "wait_sms":
                return {"status": "pending"}

            # ❌ error case
            if data.get("error_code"):
                return {
                    "status": "error",
                    "error": data.get("error_msg")
                }

            # ✅ success
            if "sms_code" in data:
                return {
                    "status": "received",
                    "otp": data["sms_code"]
                }

            return {"status": "unknown"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    # =========================
    # ❌ SET STATUS (FIXED)
    # =========================
    def set_status(self, request_id: str, status: str):

        try:
            res = requests.get(
                self.BASE_URL + "set-status",
                params={
                    "token": self.token,
                    "request_id": request_id,
                    "status": status   # ready / close / reject / used
                },
                timeout=10
            )

            data = res.json()
            return data.get("success", False)

        except Exception:
            return False

    # =========================
    # 🌍 COUNTRIES (FIXED)
    # =========================
    def get_countries(self):

        try:
            res = requests.get(
                self.BASE_URL + "countries",
                params={"token": self.token},
                timeout=10
            )

            return res.json()

        except Exception as e:
            return {"error": str(e)}

    # =========================
    # 📱 SERVICES / APPS (FIXED)
    # =========================
    def get_services(self):

        try:
            res = requests.get(
                self.BASE_URL + "applications",
                params={"token": self.token},
                timeout=10
            )

            return res.json()

        except Exception as e:
            return {"error": str(e)}

    # =========================
    # 💲 PRICES (useful for UI)
    # =========================
    def get_prices(self, country_id: str = None):

        try:
            params = {"token": self.token}
            if country_id:
                params["country_id"] = country_id

            res = requests.get(
                self.BASE_URL + "get-prices",
                params=params,
                timeout=10
            )

            return res.json()

        except Exception as e:
            return {"error": str(e)}
