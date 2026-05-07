from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "profile_menu")
async def profile_menu(callback: CallbackQuery):

    user = callback.from_user

    text = f"""
<b>👤 Profile</b>

ID: <code>{user.id}</code>
Username: @{user.username}
"""

    await callback.message.edit_text(text)

    await callback.answer()