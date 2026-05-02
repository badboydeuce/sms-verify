
from app.services.providers.smsman import SMSManProvider

class SMSService:
    def __init__(self):
        self.provider = SMSManProvider()

    def buy_number(self, country_id, app_id):
        res = self.provider.get_number(country_id, app_id)
        if "request_id" not in res:
            return {"error": "Failed"}
        return res

    def check_sms(self, request_id):
        return self.provider.get_sms(request_id)
