
import requests
from app.config import settings

class SMSManProvider:
    BASE_URL = "https://api.sms-man.com/control/"

    def __init__(self):
        self.token = settings.SMSMAN_API_KEY

    def get_number(self, country_id, application_id):
        return requests.get(self.BASE_URL+"get-number", params={
            "token": self.token,
            "country_id": country_id,
            "application_id": application_id
        }).json()

    def get_sms(self, request_id):
        return requests.get(self.BASE_URL+"get-sms", params={
            "token": self.token,
            "request_id": request_id
        }).json()

    def set_status(self, request_id, status):
        return requests.get(self.BASE_URL+"set-status", params={
            "token": self.token,
            "request_id": request_id,
            "status": status
        }).json()
