from pydantic import BaseModel


class VerifyPaymentSchema(
    BaseModel
):

    reference: str
