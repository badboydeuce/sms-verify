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
        """
        Fetches LIVE prices from SMS-Man → converts USD to NGN → applies markup.
        This is the main function the bot should call for displaying prices.
        """
        try:
            raw_prices = await SMSManActivation.get_prices(country_id)

            result = []

            for app_id, data in raw_prices.items():
                try:
                    base_cost_usd = float(data["cost"])  # ✅ SMS-Man price in USD

                    # ✅ Convert USD -> NGN then apply 25% markup
                    final_price_ngn = await convert_and_markup(base_cost_usd)

                    result.append({
                        "application_id": str(data["application_id"]),
                        "application": data.get("application", "Unknown"),
                        "base_price": base_cost_usd,        # Original USD price
                        "price": float(final_price_ngn),    # Final NGN price shown to user
                        "count": int(data.get("count", 0)),
                        "currency": "NGN"
                    })
                except (KeyError, ValueError, TypeError):
                    continue

            result.sort(key=lambda x: x["application"].lower())
            return result

        except Exception:
            raise

    # ===================== LEGACY (raw prices, no markup) =====================
    @staticmethod
    async def get_prices(country_id: int | str) -> list[dict]:
        """Legacy method - returns raw USD prices without markup or conversion"""
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
    async def buy_activation_number(country_id: int | str, application_id: int | str) -> dict:
        return await SMSManActivation.get_number(country_id, application_id)

    @staticmethod
    async def get_activation_sms(request_id: int) -> dict:
        return await SMSManActivation.get_sms(request_id)

    # ===================== RENTAL =====================
    @staticmethod
    async def rent_number(country_id: int | str, rent_type: str, time: int) -> dict:
        return await SMSManRental.get_number(country_id, rent_type, time)

    @staticmethod
    async def get_rental_price_ngn(base_price_usd: float) -> Decimal:
        """Convert rental price USD -> NGN and apply rental markup"""
        return await convert_and_markup(base_price_usd, rental=True)