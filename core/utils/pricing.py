from decimal import Decimal


MARKUP_PERCENT = Decimal("1.5")


def apply_markup(price: Decimal) -> Decimal:

    final_price = (
        price * (
            Decimal("1")
            + (
                MARKUP_PERCENT / Decimal("100")
            )
        )
    )

    return final_price.quantize(
        Decimal("0.01")
    )