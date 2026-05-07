from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)

from bot.callback_factories.orders import (
    OrderCallback
)


def activation_order_keyboard(
    order_id: int
):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🔄 Refresh OTP",
        callback_data=OrderCallback(
            action="refresh",
            order_id=order_id
        ).pack()
    )

    kb.button(
        text="❌ Cancel",
        callback_data=OrderCallback(
            action="cancel",
            order_id=order_id
        ).pack()
    )

    kb.adjust(1)

    return kb.as_markup()


def rental_order_keyboard(
    order_id: int
):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📨 Check SMS",
        callback_data=OrderCallback(
            action="sms",
            order_id=order_id
        ).pack()
    )

    kb.button(
        text="❌ Close Rental",
        callback_data=OrderCallback(
            action="close",
            order_id=order_id
        ).pack()
    )

    kb.adjust(1)

    return kb.as_markup()
