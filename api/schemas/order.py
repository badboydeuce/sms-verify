from pydantic import BaseModel


class CancelOrderSchema(
    BaseModel
):

    order_id: int
