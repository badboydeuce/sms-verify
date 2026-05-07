from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.buy import (
    buy_menu_keyboard
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

Choose service type:
""",
        reply_markup=buy_menu_keyboard()
    )

    await callback.answer()
