# core/utils/currency.py

from decimal import Decimal

# ====================== MARKUP CONFIG ======================

MARKUP_PERCENT = Decimal("100.0")        # 25% profit margin
RENTAL_MARKUP_PERCENT = Decimal("50.0")

# ====================== HARDCODED FX ======================

HARDCODED_RUB_TO_NGN = Decimal("19")  # ✅ 1 RUB ≈ ₦13.5 (adjust as needed)

# ====================== EXCHANGE RATE ======================

async def get_exchange_rate(
    from_currency: str,
    to_currency: str = "NGN"
) -> Decimal:
    rates = {
        "RUB_NGN": HARDCODED_RUB_TO_NGN,
    }
    cache_key = f"{from_currency}_{to_currency}"
    return rates.get(cache_key, Decimal("1.0"))

# ====================== MARKUP ======================

def apply_markup(price: Decimal) -> Decimal:
    final_price = price * (
        Decimal("1") + (MARKUP_PERCENT / Decimal("100"))
    )
    return final_price.quantize(Decimal("0.01"))


def apply_rental_markup(price: Decimal) -> Decimal:
    final_price = price * (
        Decimal("1") + (RENTAL_MARKUP_PERCENT / Decimal("100"))
    )
    return final_price.quantize(Decimal("0.01"))

# ====================== CONVERT + MARKUP ======================

async def convert_and_markup(
    amount_rub: float,      # ✅ renamed from amount_usd
    rental: bool = False
) -> Decimal:

    rate = await get_exchange_rate("RUB", "NGN")

    amount_ngn = Decimal(str(amount_rub)) * rate

    if rental:
        return apply_rental_markup(amount_ngn)

    return apply_markup(amount_ngn)
