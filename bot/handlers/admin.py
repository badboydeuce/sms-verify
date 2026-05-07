from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.handlers.filters.admin import (
    AdminFilter
)

from bot.keyboards.admin import (
    admin_keyboard
)

router = Router()


@router.message(
    Command("admin"),
    AdminFilter()
)
async def admin_panel(
    message: Message
):

    await message.answer(
        "<b>🛠 Admin Panel</b>",
        reply_markup=admin_keyboard()
    )
