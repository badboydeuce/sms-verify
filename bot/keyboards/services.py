# bot/keyboards/services.py

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback_factories.buy import BuyCallback


def services_keyboard(services, country_id, search: str = ""):

    kb = InlineKeyboardBuilder()

    # Filter by search term if provided
    if search:
        filtered = [
            s for s in services
            if search.lower() in s["name"].lower()
        ]
    else:
        filtered = services

    for service in filtered[:40]:
        kb.button(
            text=f"{service['name']} ₦{service['price']}",
            callback_data=BuyCallback(
                action="service",
                value=f"{country_id}_{service['id']}"
            ).pack()
        )

    # Search button
    kb.button(
        text="🔍 Search Service",
        callback_data=BuyCallback(
            action="search_service",
            value=country_id
        ).pack()
    )

    kb.button(
        text="🔙 Back",
        callback_data=BuyCallback(action="type", value="activation").pack()
    )

    kb.adjust(1)

    return kb.as_markup()
