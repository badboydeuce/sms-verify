from aiogram import Router, types
from app.bot.keyboards.main import main_menu

router = Router()


@router.message(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer(
        "Welcome to DeuceVerify 🚀",
        reply_markup=main_menu()
    )