from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):

    text = """
<b>📱 Buy Number</b>

Choose service type:
"""

    await callback.message.edit_text(
        text
    )

    await callback.answer()