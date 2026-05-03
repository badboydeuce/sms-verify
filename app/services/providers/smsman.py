import requests
from app.config import settings


class SMSManProvider:
    BASE_URL = "https://api.sms-man.com/control/"

    def __init__(self):
        self.token = settings.SMSMAN_API_KEY

    # =========================
    # 📞 BUY NUMBER
    # =========================
    def get_number(self, country_id: str, service_id: str) -> dict:
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
                "request_id": str(data["request_id"]),
                "number": data["number"]
            }

        except Exception as e:
            return {"error": str(e)}

    # =========================
    # 📩 GET SMS
    # =========================
    def get_sms(self, request_id: str) -> dict:
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
                    "code": data.get("sms_code")
                }

            return {"status": "error"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    # =========================
    # ❌ CANCEL NUMBER
    # =========================
    def set_status(self, request_id: str, status: str) -> bool:
        try:
            res = requests.get(
                self.BASE_URL + "set-status",
                params={
                    "token": self.token,
                    "request_id": request_id,
                    "status": status
                },
                timeout=10
            )

            data = res.json()
            return data.get("status") == "success"

        except Exception:
            return False

    # =========================
    # 🌍 COUNTRIES
    # =========================
    def get_countries(self) -> dict:
        try:
            res = requests.get(
                self.BASE_URL + "get-countries",
                params={"token": self.token},
                timeout=10
            )

            data = res.json()

            return {str(k): v for k, v in data.get("countries", {}).items()}

        except Exception:
            return {}

    # =========================
    # 📱 SERVICES
    # =========================
    def get_services(self, country_id: str) -> dict:
        try:
            res = requests.get(
                self.BASE_URL + "get-services",
                params={
                    "token": self.token,
                    "country_id": country_id
                },
                timeout=10
            )

            data = res.json()

            return {str(k): v for k, v in data.get("services", {}).items()}

        except Exception:
            return {}
