from aiogram.filters.callback_data import (
    CallbackData
)


class BuyCallback(CallbackData, prefix="buy"):

    action: str
    value: str
    page: int = 1
