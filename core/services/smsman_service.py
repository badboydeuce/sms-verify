# core/services/smsman_service.py

from decimal import Decimal
from core.smsman.activation import SMSManActivation
from core.smsman.rental import SMSManRental
from core.utils.currency import convert_and_markup, apply_rental_markup


class SMSManService:

    # ===================== COUNTRIES =====================
    @staticmethod
    async def get_countries() -> dict:
        return await SMSManActivation.get_countries()

    # ===================== LIVE PRICES WITH MARKUP =====================
    @staticmethod
    async def get_prices_with_markup(country_id: int | str) -> list[dict]:
        try:
            raw_prices = await SMSManActivation.get_prices(country_id)

            result = []

            for app_id, data in raw_prices.items():
                try:
                    base_cost_rub = float(data["cost"])

                    final_price_ngn = await convert_and_markup(base_cost_rub)

                    result.append({
                        "application_id": str(data["application_id"]),
                        "application": data.get("application", "Unknown"),
                        "base_price": base_cost_rub,
                        "price": float(final_price_ngn),
                        "count": int(data.get("count", 0)),
                        "currency": "NGN"
                    })
                except (KeyError, ValueError, TypeError):
                    continue

            result.sort(key=lambda x: x["application"].lower())
            return result

        except Exception:
            raise

    # ===================== LEGACY =====================
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
            except:
                continue

        result.sort(key=lambda x: x["application"])
        return result

    # ===================== ACTIVATION =====================
    @staticmethod
    async def buy_activation_number(
        country_id: int | str,
        application_id: int | str
    ) -> dict:
        return await SMSManActivation.get_number(country_id, application_id)

    @staticmethod
    async def get_activation_sms(request_id: int) -> dict:
        return await SMSManActivation.get_sms(request_id)

    # ===================== RENTAL COUNTRIES =====================
    @staticmethod
    async def get_rental_countries(rent_type: str, time: int) -> list[dict]:
        """
        Returns available countries for rental with count > 0,
        prices converted from RUB to NGN with rental markup.
        """
        data = await SMSManRental.get_limits(rent_type, time)

        if not data or "limits" not in data:
            return []

        result = []

        for item in data["limits"]:
            if int(item.get("count", 0)) == 0:
                continue  # skip unavailable countries

            price_ngn = await convert_and_markup(
                float(item["cost"]),
                rental=True
            )

            result.append({
                "country_id": str(item["country_id"]),
                "count": int(item["count"]),
                "cost_rub": float(item["cost"]),
                "price_ngn": float(price_ngn)
            })

        return result

    # ===================== RENTAL =====================
    @staticmethod
    async def rent_number(
        country_id: int | str,
        rent_type: str,
        time: int
    ) -> dict:
        return await SMSManRental.get_number(country_id, rent_type, time)

    @staticmethod
    async def get_rental_limits(
        country_id: str,
        rent_type: str,
        time: int
    ) -> dict:
        return await SMSManRental.get_limits(rent_type, time, country_id=country_id)

    @staticmethod
    async def get_rental_price_ngn(base_price_rub: float) -> Decimal:
        return await convert_and_markup(base_price_rub, rental=True)

    @staticmethod
    async def get_rental_sms(request_id: int) -> dict:
        return await SMSManRental.get_sms(request_id)

    @staticmethod
    async def get_all_rental_sms(request_id: int) -> dict:
        return await SMSManRental.get_all_sms(request_id)
