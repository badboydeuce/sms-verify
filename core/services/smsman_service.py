from decimal import Decimal
from core.smsman.activation import SMSManActivation
from core.smsman.rental import SMSManRental


class SMSManService:

    # ================== MARKUP CONFIG ==================
    MARKUP_PERCENT = 25.0          # ← Changed from 2500 (was too high)
    RENTAL_MARKUP_PERCENT = 30.0   # Rental usually has higher margin

    @staticmethod
    def apply_markup(base_price: float) -> Decimal:
        """Apply user markup and return clean price"""
        final_price = base_price * (1 + SMSManService.MARKUP_PERCENT / 100)
        return Decimal(str(round(final_price, 2)))   # Round to 2 decimals

    @staticmethod
    def apply_rental_markup(base_price: float) -> Decimal:
        final_price = base_price * (1 + SMSManService.RENTAL_MARKUP_PERCENT / 100)
        return Decimal(str(round(final_price, 2)))

    # ===================== COUNTRIES =====================
    @staticmethod
    async def get_countries() -> dict:
        return await SMSManActivation.get_countries()

    # ===================== LIVE PRICES WITH MARKUP =====================
    @staticmethod
    async def get_prices_with_markup(country_id: int | str) -> list[dict]:
        """
        Fetches LIVE prices from SMS-Man → applies markup → returns ready for bot.
        This is the main function the bot should call for displaying prices.
        """
        try:
            # Call through your API route (which has very short cache)
            raw_prices = await SMSManActivation.get_prices(country_id)

            result = []

            for app_id, data in raw_prices.items():
                try:
                    base_cost = float(data["cost"])

                    marked_price = SMSManService.apply_markup(base_cost)

                    result.append({
                        "application_id": str(data["application_id"]),
                        "application": data.get("application", "Unknown"),
                        "base_price": base_cost,           # Original SMS-Man price
                        "price": float(marked_price),      # Final price shown to user
                        "count": int(data.get("count", 0)),
                        "currency": "NGN"
                    })
                except (KeyError, ValueError, TypeError):
                    continue

            # Sort alphabetically
            result.sort(key=lambda x: x["application"].lower())

            return result

        except Exception as e:
            # Let the caller handle the exception (better logging in handler)
            raise

    # ===================== EXISTING METHODS (kept) =====================
    @staticmethod
    async def get_prices(country_id: int | str) -> list[dict]:
        """Legacy method - returns raw without markup"""
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

    @staticmethod
    async def buy_activation_number(country_id: int | str, application_id: int | str) -> dict:
        return await SMSManActivation.get_number(country_id, application_id)

    @staticmethod
    async def get_activation_sms(request_id: int) -> dict:
        return await SMSManActivation.get_sms(request_id)

    @staticmethod
    async def rent_number(country_id: int | str, rent_type: str, time: int) -> dict:
        return await SMSManRental.get_number(country_id, rent_type, time)
