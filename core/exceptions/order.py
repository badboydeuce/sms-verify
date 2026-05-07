from core.exceptions.base import (
    DeuceVerifyException
)


class OrderExpired(
    DeuceVerifyException
):

    default_message = (
        "Order expired"
    )


class UnauthorizedOrderAccess(
    DeuceVerifyException
):

    default_message = (
        "Unauthorized order access"
    )