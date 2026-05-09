# bot/keyboards/countries.py

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback_factories.buy import BuyCallback


def countries_keyboard(countries, search: str = ""):

    kb = InlineKeyboardBuilder()

    # Filter by search term if provided
    if search:
        filtered = [
            c for c in countries
            if search.lower() in c["title"].lower()
        ]
    else:
        filtered = countries

    for country in filtered[:40]:
        kb.button(
            text=f"{country['title']}",
            callback_data=BuyCallback(
                action="country",
                value=str(country["id"])
            ).pack()
        )

    # Search button
    kb.button(
        text="🔍 Search Country",
        callback_data=BuyCallback(action="search_country", value="start").pack()
    )

    kb.button(
        text="🔙 Back",
        callback_data=BuyCallback(action="type", value="activation").pack()
    )

    kb.adjust(2)

    return kb.as_markup()


def countries_keyboard_filtered(countries, search: str):
    return countries_keyboard(countries, search=search)
