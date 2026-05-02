
from abc import ABC, abstractmethod

class SMSProvider(ABC):
    @abstractmethod
    def get_number(self, country_id, application_id): pass

    @abstractmethod
    def get_sms(self, request_id): pass

    @abstractmethod
    def set_status(self, request_id, status): pass
