from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import (
    main_menu_keyboard
)

router = Router()


@router.message(CommandStart())
async def start_handler(
    message: Message
):

    text = """
<b>Welcome to DeuceVerify</b>

Virtual Number SMS Verification Platform

• One-Time SMS
• Rental Numbers
• Compatible API
"""

    await message.answer(
        text,
        reply_markup=main_menu_keyboard()
    )
