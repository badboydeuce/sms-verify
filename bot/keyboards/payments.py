from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)


def payment_keyboard(url: str):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="💳 Pay Now",
        url=url
    )

    return kb.as_markup()
