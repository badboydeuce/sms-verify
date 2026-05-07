from core.exceptions.base import (
    DeuceVerifyException
)


class InvalidWebhookSignature(
    DeuceVerifyException
):

    default_message = (
        "Invalid Paystack signature"
    )


class TransactionVerificationFailed(
    DeuceVerifyException
):

    default_message = (
        "Transaction verification failed"
    )