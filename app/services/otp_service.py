# app/services/otp_service.py

import time
from app.services.smsman import SMSManProvider
from app.core.config import settings


class OTPService:

    def __init__(self):
        self.sms = SMSManProvider()

    # =========================
    # 📩 POLL OTP
    # =========================
    def wait_for_otp(self, request_id: str, timeout: int = None):

        timeout = timeout or settings.OTP_EXPIRY_SECONDS
        start = time.time()

        while time.time() - start < timeout:

            res = self.sms.get_sms(request_id)

            if res.get("status") == "received":
                return res["otp"]

            time.sleep(5)

        return None
