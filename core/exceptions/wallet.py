from core.exceptions.base import (
    DeuceVerifyException
)


class InsufficientBalance(
    DeuceVerifyException
):

    default_message = (
        "Insufficient balance"
    )


class MinimumFundingError(
    DeuceVerifyException
):

    default_message = (
        "Minimum funding is ₦1,500"
    )