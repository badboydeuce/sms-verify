from aiogram.filters.callback_data import (
    CallbackData
)


class OrderCallback(
    CallbackData,
    prefix="order"
):

    action: str
    order_id: int
