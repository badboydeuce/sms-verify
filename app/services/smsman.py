# app/services/smsman.py

import requests
from app.core.config import settings


class SMSManProvider:
    BASE_URL = "https://api.sms-man.com/control/"

    def __init__(self):
        self.token = settings.SMSMAN_API_KEY

    # =========================
    # 📞 BUY NUMBER
    # =========================
    def get_number(self, country_id: str, service_id: str):
        try:
            res = requests.get(
                self.BASE_URL + "get-number",
                params={
                    "token": self.token,
                    "country_id": country_id,
                    "service": service_id
                },
                timeout=10
            )

            data = res.json()

            if data.get("status") != "success":
                return {"error": data}

            return {
                "request_id": data["request_id"],
                "number": data["number"]
            }

        except Exception as e:
            return {"error": str(e)}

    # =========================
    # 📩 GET SMS
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

            if data.get("status") == "wait":
                return {"status": "pending"}

            if data.get("status") == "success":
                return {
                    "status": "received",
                    "otp": data.get("sms_code")
                }

            return {"status": "error"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    # =========================
    # ❌ CANCEL NUMBER
    # =========================
    def cancel(self, request_id: str):
        try:
            res = requests.get(
                self.BASE_URL + "set-status",
                params={
                    "token": self.token,
                    "request_id": request_id,
                    "status": "cancel"
                },
                timeout=10
            )

            return res.json().get("status") == "success"

        except Exception:
            return False

    # =========================
    # 🌍 COUNTRIES
    # =========================
    def get_countries(self):
        try:
            res = requests.get(
                self.BASE_URL + "get-countries",
                params={"token": self.token},
                timeout=10
            )

            return res.json()

        except Exception:
            return {}

    # =========================
    # 📱 SERVICES
    # =========================
    def get_services(self, country_id: str):
        try:
            res = requests.get(
                self.BASE_URL + "get-services",
                params={
                    "token": self.token,
                    "country_id": country_id
                },
                timeout=10
            )

            return res.json()

        except Exception:
            return {}
