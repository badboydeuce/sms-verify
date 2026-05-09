import asyncio

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

        # API returns a list [{"id": "1", "name": "...", "code": "..."}]
        if isinstance(raw, list):
            return {str(item["id"]): item for item in raw}

        return raw

    @staticmethod
    async def get_prices(country_id: int | str) -> list[dict]:
        """
        Normalizes raw prices into a flat list:
        [
            {
                "application_id": "1",
                "application": "Vkontakte",
                "price": 15.0,
                "count": 6455
            },
            ...
        ]
        """
        raw_prices, services_map = await asyncio.gather(
            SMSManActivation.get_prices(country_id),
            SMSManService.get_services()
        )

        # Raw: {"app_id": {"cost": "15", "count": 6455}, ...}
        # country_id key may or may not be present depending on API version
        if str(country_id) in raw_prices:
            country_prices = raw_prices[str(country_id)]
        else:
            country_prices = raw_prices

        result = []

        for app_id, data in country_prices.items():
            service = services_map.get(str(app_id))

            if not service:
                continue

            try:
                result.append({
                    "application_id": str(app_id),
                    "application": service["name"],
                    "price": float(data["cost"]),
                    "count": int(data.get("count", 0))
                })
            except (KeyError, ValueError):
                continue

        # Sort by name for consistent display
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
