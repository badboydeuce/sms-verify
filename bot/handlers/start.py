# bot/handlers/start.py

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.main_menu import main_menu_keyboard
from core.database.session import AsyncSessionLocal
from core.services.user_service import UserService

router = Router()


def currency_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇳🇬 Nigerian Naira (NGN)", callback_data="set_currency_NGN")
    kb.button(text="🇺🇸 US Dollar (USD)", callback_data="set_currency_USD")
    kb.adjust(1)
    return kb.as_markup()


@router.message(CommandStart())
async def start_handler(message: Message, db_user):

    # ✅ Only ask currency on first start — if not set yet
    if not hasattr(db_user, 'currency') or db_user.currency is None:
        await message.answer(
            "<b>👋 Welcome to DeuceVerify!</b>\n\n"
            "Before we begin, please select your preferred display currency:",
            reply_markup=currency_keyboard(),
            parse_mode="HTML"
        )
        return

    await message.answer(
        "<b>Welcome to DeuceVerify</b>\n\n"
        "Virtual Number SMS Verification Platform\n\n"
        "• One-Time SMS\n• Rental Numbers\n• Compatible API",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


# ====================== CURRENCY SELECTION ======================
@router.callback_query(F.data.startswith("set_currency_"))
async def set_currency(callback: CallbackQuery, db_user):
    currency = callback.data.replace("set_currency_", "")

    async with AsyncSessionLocal() as db:
        user = await UserService.get_user_by_telegram_id(db, db_user.telegram_id)
        user.currency = currency
        await db.commit()

    flag = "🇳🇬" if currency == "NGN" else "🇺🇸"

    await callback.message.edit_text(
        f"<b>Welcome to DeuceVerify</b>\n\n"
        f"Currency set to {flag} <b>{currency}</b>\n\n"
        f"Virtual Number SMS Verification Platform\n\n"
        f"• One-Time SMS\n• Rental Numbers\n• Compatible API",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
