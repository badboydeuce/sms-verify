from aiogram import Router
from aiogram.types import Message

from bot.keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message()
async def start_handler(message: Message):

    text = """
<b>Welcome to DeuceVerify</b>

Virtual Number SMS Verification Platform

• One-Time SMS
• Number Rentals
• Compatible API
• Fast OTP Delivery
"""

    await message.answer(
        text,
        reply_markup=main_menu_keyboard()
    )