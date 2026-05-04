# app/services/otp_service.py

import time
from app.services.smsman import SMSManProvider
from app.core.config import settings


class OTPService:

    def __init__(self):
        self.sms = SMSManProvider()

    # =========================
    # 📩 POLL OTP (IMPROVED)
    # =========================
    def wait_for_otp(self, request_id: str, timeout: int = None):

        timeout = timeout or settings.OTP_EXPIRY_SECONDS
        start = time.time()

        # 🚀 Optional upgrade: adaptive polling delay (reduces API spam)
        delay = 3

        while time.time() - start < timeout:

            res = self.sms.get_sms(request_id)

            # ✅ OTP received
            if isinstance(res, dict) and "sms_code" in res:
                return res["sms_code"]

            # ⏳ still waiting (SMS-man standard response)
            if res.get("error_code") == "wait_sms":
                time.sleep(delay)

                # 🚀 gradually increase delay (3s → 10s max)
                delay = min(delay + 2, 10)
                continue

            # ❌ unexpected API error (fail fast)
            if isinstance(res, dict) and res.get("error_code"):
                raise Exception(res.get("error_msg"))

            # fallback safety sleep
            time.sleep(delay)

        # ⛔ timeout reached
        return None
