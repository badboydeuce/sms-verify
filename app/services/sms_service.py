from app.services.providers.smsman import SMSManProvider


class SMSService:

    def __init__(self):
        self.provider = SMSManProvider()

    def get_countries(self):
        return self.provider.get_countries()

    def get_services(self, country_id):
        return self.provider.get_services(country_id)

    def buy_number(self, country_id, service_id):
        return self.provider.get_number(country_id, service_id)

    def get_sms(self, request_id):
        return self.provider.get_sms(request_id)

    def cancel_number(self, request_id):
        return self.provider.set_status(request_id, "cancel")
