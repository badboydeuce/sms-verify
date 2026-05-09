from core.smsman.activation import SMSManActivation
from core.smsman.rental import SMSManRental


class SMSManService:

    MARKUP_PERCENT = 1.5

    @staticmethod
    def apply_markup(price: float) -> float:
        return round(price * (1 + SMSManService.MARKUP_PERCENT / 100), 2)

    @staticmethod
    async def get_countries() -> dict:
        """
        Returns dict keyed by country_id:
        {"3": {"id": "3", "title": "China", "code": "CN"}, ...}
        """
        return await SMSManActivation.get_countries()

    @staticmethod
    async def get_services() -> dict:
        """
        Returns dict keyed by service_id:
        {"1": {"id": "1", "name": "Vkontakte", "code": "vk"}, ...}
        """
        raw = await SMSManActivation.get_services()

        if isinstance(raw, list):
            return {str(item["id"]): item for item in raw}

        return raw

    @staticmethod
    async def get_prices(country_id: int | str) -> list[dict]:
        """
        Normalizes raw prices into a flat list:
        [
            {
                "application_id": "125",
                "application": "Twitter",
                "price": 11.38,
                "count": 13171
            },
            ...
        ]
        """
        raw = await SMSManActivation.get_prices(country_id)

        result = []

        for app_id, data in raw.items():

            try:

                result.append({
                    "application_id": str(data["application_id"]),
                    "application": data["application"],
                    "price": float(data["cost"]),
                    "count": int(data.get("count", 0))
                })

            except (KeyError, ValueError):
                continue

        result.sort(key=lambda x: x["application"])

        return result

    @staticmethod
    async def buy_activation_number(
        country_id: int | str,
        application_id: int | str
    ) -> dict:
        return await SMSManActivation.get_number(country_id, application_id)

    @staticmethod
    async def get_activation_sms(request_id: int) -> dict:
        return await SMSManActivation.get_sms(request_id)

    @staticmethod
    async def rent_number(
        country_id: int | str,
        rent_type: str,
        time: int
    ) -> dict:
        return await SMSManRental.get_number(country_id, rent_type, time)

    @staticmethod
    async def get_rental_sms(request_id: int) -> dict:
        return await SMSManRental.get_all_sms(request_id)
