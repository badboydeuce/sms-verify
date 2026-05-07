from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)

from bot.callback_factories.admin import (
    AdminCallback
)


def admin_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="👥 Users",
        callback_data=AdminCallback(
            action="users"
        ).pack()
    )

    kb.button(
        text="📦 Orders",
        callback_data=AdminCallback(
            action="orders"
        ).pack()
    )

    kb.button(
        text="💰 Revenue",
        callback_data=AdminCallback(
            action="revenue"
        ).pack()
    )

    kb.adjust(1)

    return kb.as_markup()
