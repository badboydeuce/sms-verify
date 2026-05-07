from aiogram import Router
from aiogram.types import Message

from bot.filters.admin import AdminFilter

router = Router()


@router.message(AdminFilter(), commands=["admin"])
async def admin_panel(message: Message):

    await message.answer(
        "<b>🛠 Admin Panel</b>"
    )