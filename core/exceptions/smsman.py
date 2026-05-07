from core.exceptions.base import (
    DeuceVerifyException
)


class SMSManAPIError(
    DeuceVerifyException
):

    default_message = (
        "SMS-Man API error"
    )


class NumberUnavailable(
    DeuceVerifyException
):

    default_message = (
        "Number not available"
    )