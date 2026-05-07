from aiogram.filters.callback_data import (
    CallbackData
)


class WalletCallback(
    CallbackData,
    prefix="wallet"
):

    action: str
