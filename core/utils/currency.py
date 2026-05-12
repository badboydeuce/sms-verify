# core/utils/currency.py

import os
import httpx
import time
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# ====================== MARKUP CONFIG ======================
MARKUP_PERCENT = Decimal("25.0")
RENTAL_MARKUP_PERCENT = Decimal("30.0")

# ====================== FX CACHE ======================
_fx_cache = {}
_fx_ttl = 7200  # ✅ 2 hours


# ====================== EXCHANGE RATE ======================
async def get_exchange_rate(from_currency: str, to_currency: str = "NGN") -> Decimal:
    """Fetch live exchange rate from exchangerate-api.com"""
    cache_key = f"{from_currency}_{to_currency}"
    now = time.time()

    if cache_key in _fx_cache:
        cached_at, rate = _fx_cache[cache_key]
        if now - cached_at < _fx_ttl:
            logger.info(f"Using cached rate {from_currency} -> {to_currency}: {rate}")
            return rate

    # ✅ Hardcode key directly to confirm it works, then switch back to env
    api_key = EXCHANGE_RATE_API_KEY or "60240a6d53589833a7cb80b5"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"

    logger.info(f"Fetching exchange rate from: {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            logger.info(f"FX API status: {response.status_code}")
            data = response.json()
            logger.info(f"FX API response: {data}")

            if data.get("result") != "success":
                raise ValueError(f"API error: {data.get('error-type', 'unknown')}")

            rate = Decimal(str(data["conversion_rates"][to_currency]))  # ✅ correct key
            _fx_cache[cache_key] = (now, rate)
            logger.info(f"Exchange rate {from_currency} -> {to_currency}: {rate}")
            return rate

    except Exception as e:
        logger.error(f"Failed to fetch exchange rate: {e}")
        fallbacks = {
            "USD_NGN": Decimal("1580.0"),
        }
        return fallbacks.get(cache_key, Decimal("1.0"))


# ====================== MARKUP ======================
def apply_markup(price: Decimal) -> Decimal:
    final_price = price * (Decimal("1") + (MARKUP_PERCENT / Decimal("100")))
    return final_price.quantize(Decimal("0.01"))


def apply_rental_markup(price: Decimal) -> Decimal:
    final_price = price * (Decimal("1") + (RENTAL_MARKUP_PERCENT / Decimal("100")))
    return final_price.quantize(Decimal("0.01"))


# ====================== COMBINED: CONVERT + MARKUP ======================
async def convert_and_markup(amount_usd: float, rental: bool = False) -> Decimal:
    """Convert USD to NGN then apply markup. Main function to call."""
    rate = await get_exchange_rate("USD", "NGN")
    amount_ngn = Decimal(str(amount_usd)) * rate

    if rental:
        return apply_rental_markup(amount_ngn)
    return apply_markup(amount_ngn)