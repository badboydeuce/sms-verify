import requests
import os
import time


class SMSService:
    def __init__(self):
        self.api_key = os.getenv("SMSMAN_API_KEY")
        self.base_url = "https://api.sms-man.com/control"

        if not self.api_key:
            raise ValueError("❌ SMSMAN_API_KEY not set in environment")

    # =========================
    # 🌍 GET COUNTRIES
    # =========================
    def get_countries(self) -> dict:
        """
        Returns:
        {
            "1": "Russia",
            "2": "Ukraine",
            ...
        }
        """
        url = f"{self.base_url}/get-countries"
        params = {"token": self.api_key}

        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            if not data or "countries" not in data:
                return {}

            return {str(k): v for k, v in data["countries"].items()}

        except Exception as e:
            print(f"❌ get_countries error: {e}")
            return {}

    # =========================
    # 📱 GET SERVICES
    # =========================
    def get_services(self, country_id: str) -> dict:
        """
        Returns:
        {
            "tg": "Telegram",
            "wa": "WhatsApp",
            ...
        }
        """
        url = f"{self.base_url}/get-services"
        params = {
            "token": self.api_key,
            "country_id": country_id
        }

        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            if not data or "services" not in data:
                return {}

            return {str(k): v for k, v in data["services"].items()}

        except Exception as e:
            print(f"❌ get_services error: {e}")
            return {}

    # =========================
    # 📞 BUY NUMBER
    # =========================
    def buy_number(self, country_id: str, service_id: str) -> dict:
        """
        Returns:
        {
            "request_id": "123456",
            "number": "+1234567890"
        }
        """
        url = f"{self.base_url}/get-number"
        params = {
            "token": self.api_key,
            "country_id": country_id,
            "service": service_id
        }

        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            if not data or data.get("status") != "success":
                return {"error": data}

            return {
                "request_id": str(data["request_id"]),
                "number": data["number"]
            }

        except Exception as e:
            print(f"❌ buy_number error: {e}")
            return {"error": str(e)}

    # =========================
    # 📩 GET SMS (OTP)
    # =========================
    def get_sms(self, request_id: str) -> str | None:
        """
        Returns OTP string or None if not available
        """
        url = f"{self.base_url}/get-sms"
        params = {
            "token": self.api_key,
            "request_id": request_id
        }

        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            if not data:
                return None

            if data.get("status") == "wait":
                return None

            if data.get("status") == "success":
                return data.get("sms_code")

            return None

        except Exception as e:
            print(f"❌ get_sms error: {e}")
            return None

    # =========================
    # ❌ CANCEL NUMBER
    # =========================
    def cancel_number(self, request_id: str) -> bool:
        """
        Returns True if cancelled
        """
        url = f"{self.base_url}/set-status"
        params = {
            "token": self.api_key,
            "request_id": request_id,
            "status": "cancel"
        }

        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            return data.get("status") == "success"

        except Exception as e:
            print(f"❌ cancel_number error: {e}")
            return False

    # =========================
    # 🔄 OPTIONAL: AUTO POLL OTP
    # =========================
    def wait_for_sms(self, request_id: str, timeout: int = 120):
        """
        Polls SMS every 5 seconds until received or timeout
        """
        start = time.time()

        while time.time() - start < timeout:
            sms = self.get_sms(request_id)

            if sms:
                return sms

            time.sleep(5)

        return None
