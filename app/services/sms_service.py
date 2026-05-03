# app/services/sms_service.py

from app.services.providers.smsman import SMSManProvider
import logging

logger = logging.getLogger(__name__)


class SMSService:

    def __init__(self):
        self.provider = SMSManProvider()

    # =========================
    # 🌍 COUNTRIES
    # =========================
    def get_countries(self):
        return self.provider.get_countries()

    # =========================
    # 📲 SERVICES
    # =========================
    def get_services(self, country_id):
        return self.provider.get_services(country_id)

    # =========================
    # 📞 BUY NUMBER
    # =========================
    def buy_number(self, country_id, service_id):
        """
        Returns:
        {
            success: bool,
            order_id: str,
            number: str
        }
        """

        try:
            result = self.provider.get_number(country_id, service_id)

            if not result:
                return {"success": False, "error": "No response from provider"}

            return result

        except Exception as e:
            logger.exception(e)
            return {"success": False, "error": str(e)}

    # =========================
    # 📩 GET SMS / OTP
    # =========================
    def get_sms(self, request_id):
        """
        Poll SMS code for active number
        """

        try:
            return self.provider.get_sms(request_id)

        except Exception as e:
            logger.exception(e)
            return {"success": False, "error": str(e)}

    # =========================
    # ❌ CANCEL NUMBER
    # =========================
    def cancel_number(self, request_id):
        try:
            return self.provider.set_status(request_id, "cancel")

        except Exception as e:
            logger.exception(e)
            return {"success": False, "error": str(e)}