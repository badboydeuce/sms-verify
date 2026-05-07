from decimal import Decimal

from core.exceptions.wallet import (
    MinimumFundingError
)


MINIMUM_FUNDING = Decimal("1500")


def validate_funding_amount(
    amount: Decimal
):

    if amount < MINIMUM_FUNDING:

        raise MinimumFundingError()