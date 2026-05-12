# core/utils/currency.py

from decimal import Decimal

# ====================== MARKUP CONFIG ======================

MARKUP_PERCENT = Decimal("25.0")
RENTAL_MARKUP_PERCENT = Decimal("30.0")

# ====================== HARDCODED FX ======================

HARDCODED_USD_TO_NGN = Decimal("1600.0")

# ====================== EXCHANGE RATE ======================

async def get_exchange_rate(
    from_currency: str,
    to_currency: str = "NGN"
) -> Decimal:
    """
    Return hardcoded exchange rate.
    """

    rates = {
        "USD_NGN": HARDCODED_USD_TO_NGN,
    }

    cache_key = f"{from_currency}_{to_currency}"

    return rates.get(cache_key, Decimal("1.0"))

# ====================== MARKUP ======================

def apply_markup(price: Decimal) -> Decimal:
    final_price = price * (
        Decimal("1") + (
            MARKUP_PERCENT / Decimal("100")
        )
    )

    return final_price.quantize(
        Decimal("0.01")
    )


def apply_rental_markup(price: Decimal) -> Decimal:
    final_price = price * (
        Decimal("1") + (
            RENTAL_MARKUP_PERCENT / Decimal("100")
        )
    )

    return final_price.quantize(
        Decimal("0.01")
    )

# ====================== CONVERT + MARKUP ======================

async def convert_and_markup(
    amount_usd: float,
    rental: bool = False
) -> Decimal:

    rate = await get_exchange_rate(
        "USD",
        "NGN"
    )

    amount_ngn = Decimal(
        str(amount_usd)
    ) * rate

    if rental:
        return apply_rental_markup(
            amount_ngn
        )

    return apply_markup(
        amount_ngn
    )