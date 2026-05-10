# core/services/smsman_service.py

from core.smsman.activation import SMSManActivation
from core.smsman.rental import SMSManRental


class SMSManService:

    MARKUP_PERCENT = 1500

    @staticmethod
    def apply_markup(price: float) -> float:
        return round(price * (1 + SMSManService.MARKUP_PERCENT / 100), 2)

    @staticmethod
    async def get_countries() -> dict:
        return await SMSManActivation.get_countries()

    @staticmethod
    async def get_services() -> dict:
        raw = await SMSManActivation.get_services()

        if isinstance(raw, list):
            return {str(item["id"]): item for item in raw}

        return raw

    @staticmethod
    async def get_prices(country_id: int | str) -> list[dict]:
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

    @staticmethod
    async def get_rental_limits(                # ✅ added
        country_id: int | str,
        rent_type: str,
        time: int
    ) -> dict:
        return await SMSManRental.get_limits(country_id, rent_type, time)
