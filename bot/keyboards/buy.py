from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)

from bot.callback_factories.buy import (
    BuyCallback
)


def buy_menu_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📩 One-Time SMS",
        callback_data=BuyCallback(
            action="type",
            value="activation"
        ).pack()
    )

    kb.button(
        text="♻️ Rent Number",
        callback_data=BuyCallback(
            action="type",
            value="rental"
        ).pack()
    )

    kb.button(
        text="🔗 Compatible API",
        callback_data=BuyCallback(
            action="type",
            value="compatible"
        ).pack()
    )

    kb.button(
        text="🔙 Back",
        callback_data="main_menu"
    )

    kb.adjust(1)

    return kb.as_markup()


def countries_keyboard(
    countries,
    page=1
):

    kb = InlineKeyboardBuilder()

    for country in countries:

        kb.button(
            text=f"🌍 {country['name']}",
            callback_data=BuyCallback(
                action="country",
                value=str(country["id"]),
                page=page
            ).pack()
        )

    kb.button(
        text="🔙 Back",
        callback_data="buy_menu"
    )

    kb.adjust(2)

    return kb.as_markup()
