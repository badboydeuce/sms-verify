# core/services/fivesim_service.py

from decimal import Decimal
from core.fivesim.client import FiveSimClient
from core.utils.currency import convert_usd_and_markup  # ✅ was convert_and_markup


class FiveSimService:

    # ===================== COUNTRIES =====================
    @staticmethod
    async def get_countries() -> list[dict]:
        raw = await FiveSimClient.get_countries()

        result = []
        for key, data in raw.items():
            result.append({
                "name": key,
                "title": data.get("text_en", key.title()),
            })

        result.sort(key=lambda x: x["title"])
        return result

    # ===================== PRODUCTS WITH MARKUP =====================
    @staticmethod
    async def get_products_with_markup(country: str) -> list[dict]:
        raw = await FiveSimClient.get_products(country, operator="any")

        result = []
        for product_name, data in raw.items():
            if data.get("Category") != "activation":
                continue
            if int(data.get("Qty", 0)) == 0:
                continue

            price_usd = float(data.get("Price", 0))

            # ✅ 5sim prices are in USD — use USD converter
            price_ngn = await convert_usd_and_markup(price_usd)

            result.append({
                "name": product_name,
                "title": product_name.title(),
                "qty": int(data.get("Qty", 0)),
                "price_usd": price_usd,
                "price_ngn": float(price_ngn)
            })

        result.sort(key=lambda x: x["title"])
        return result

    # ===================== BUY NUMBER =====================
    @staticmethod
    async def buy_activation(
        country: str,
        product: str
    ) -> dict:
        return await FiveSimClient.buy_activation(country, product)

    # ===================== CHECK SMS =====================
    @staticmethod
    async def check_order(order_id: int) -> dict:
        return await FiveSimClient.check_order(order_id)

    # ===================== CANCEL =====================
    @staticmethod
    async def cancel_order(order_id: int) -> dict:
        return await FiveSimClient.cancel_order(order_id)

    # ===================== FINISH =====================
    @staticmethod
    async def finish_order(order_id: int) -> dict:
        return await FiveSimClient.finish_order(order_id)
