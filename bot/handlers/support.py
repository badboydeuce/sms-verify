# bot/handlers/support.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

router = Router()


@router.callback_query(F.data == "support_menu")
async def support_menu(callback: CallbackQuery):
    text = """
<b>❓ Support Center</b>

Contact admin for assistance.
Support: @DeuceVerifySupport | 
Https://t.me/DeuceVerifySuppirt
Channel: https://t.me/DeuceVerify

"""

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer("✅ Support opened")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🆘 <b>Help Menu</b>\n\n"
        "Use the buttons below to navigate the bot.",
        parse_mode="HTML"
    )