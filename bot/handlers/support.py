from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "support_menu")
async def support_menu(callback: CallbackQuery):
    text = """
<b>❓ Support</b>

Contact admin for assistance.
"""

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()