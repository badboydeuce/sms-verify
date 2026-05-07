from core.smsman.activation import SMSManActivation
from core.smsman.rental import SMSManRental


class SMSManService:

    MARKUP_PERCENT = 1.5

    @staticmethod
    def apply_markup(price):

        return round(
            price * (
                1 + (
                    SMSManService.MARKUP_PERCENT / 100
                )
            ),
            2
        )

    @staticmethod
    async def get_countries():

        response = await SMSManActivation.get_countries()

        return response

    @staticmethod
    async def get_services():

        response = await SMSManActivation.get_services()

        return response

    @staticmethod
    async def get_prices(country_id):

        response = await SMSManActivation.get_prices(
            country_id
        )

        return response

    @staticmethod
    async def buy_activation_number(
        country_id,
        application_id
    ):

        response = await SMSManActivation.get_number(
            country_id,
            application_id
        )

        return response

    @staticmethod
    async def get_activation_sms(
        request_id
    ):

        response = await SMSManActivation.get_sms(
            request_id
        )

        return response

    @staticmethod
    async def rent_number(
        country_id,
        rent_type,
        time
    ):

        response = await SMSManRental.get_number(
            country_id,
            rent_type,
            time
        )

        return response

    @staticmethod
    async def get_rental_sms(
        request_id
    ):

        response = await SMSManRental.get_all_sms(
            request_id
        )

        return response