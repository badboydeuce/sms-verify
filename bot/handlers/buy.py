from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.services.smsman_service import (
    SMSManService
)

from bot.keyboards.buy import (
    buy_menu_keyboard
)

from bot.keyboards.countries import (
    countries_keyboard
)

from bot.callback_factories.buy import (
    BuyCallback
)

router = Router()


@router.callback_query(
    F.data == "buy_menu"
)
async def buy_menu(
    callback: CallbackQuery
):

    await callback.message.edit_text(
        """
<b>📱 Buy Number</b>

Choose service:
""",
        reply_markup=buy_menu_keyboard()
    )

    await callback.answer()


@router.callback_query(
    BuyCallback.filter(
        F.action == "type"
    )
)
async def choose_type(
    callback: CallbackQuery,
    callback_data: BuyCallback
):

    if callback_data.value == "activation":

        countries = (
            await SMSManService.get_countries()
        )

        await callback.message.edit_text(
            "🌍 Select country",
            reply_markup=countries_keyboard(
                countries
            )
        )

    await callback.answer()
