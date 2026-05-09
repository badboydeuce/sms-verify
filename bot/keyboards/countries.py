from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories.buy import BuyCallback


def countries_keyboard(countries):

    kb = InlineKeyboardBuilder()

    for country in countries[:40]:

        kb.button(
            text=f"{country['title']}",
            callback_data=BuyCallback(
                action="country",
                value=str(country["id"])
            ).pack()
        )

    kb.adjust(2)

    return kb.as_markup()
