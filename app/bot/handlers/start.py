# app/bot/handlers/start.py

from aiogram import Router, types
from app.bot.keyboards.main import main_menu

router = Router()


@router.message(lambda message: message.text == "/start")
async def start_handler(message: types.Message):
    await message.answer(
        "🚀 Welcome to DeuceVerify\n\nBuy virtual numbers instantly.",
        reply_markup=main_menu()
    )
