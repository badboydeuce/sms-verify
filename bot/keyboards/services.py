from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)

from bot.callback_factories.buy import (
    BuyCallback
)


def services_keyboard(
    services,
    country_id
):

    kb = InlineKeyboardBuilder()

    for service in services[:40]:

        kb.button(
            text=(
                f"{service['name']} "
                f"₦{service['price']}"
            ),

            callback_data=BuyCallback(
                action="service",
                value=(
                    f"{country_id}_"
                    f"{service['id']}"
                )
            ).pack()
        )

    kb.adjust(1)

    return kb.as_markup()
