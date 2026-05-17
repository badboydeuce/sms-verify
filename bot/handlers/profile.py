# bot/handlers/profile.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import httpx
import logging

from core.config import API_BASE_URL
from core.database.session import AsyncSessionLocal
from core.services.user_service import UserService
from core.utils.currency import format_amount

router = Router()
logger = logging.getLogger(__name__)


def profile_keyboard(currency: str):
    kb = InlineKeyboardBuilder()
    label = "Switch to USD 🇺🇸" if currency == "NGN" else "Switch to NGN 🇳🇬"
    kb.button(text=label, callback_data="toggle_currency")
    kb.button(text="🔙 Back", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


@router.callback_query(F.data == "profile_menu")
async def profile_menu(callback: CallbackQuery):
    user = callback.from_user

    # Fetch wallet balance and currency from API
    balance_display = "N/A"
    currency = "NGN"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL.rstrip('/')}/api/wallet/balance/{user.id}"
            )
            if response.status_code == 200:
                data = response.json()
                currency = data.get("currency", "NGN")
                balance_display = format_amount(data["balance"], currency)
    except Exception as e:
        logger.error(f"Failed to fetch balance for {user.id}: {e}")

    currency_flag = "🇺🇸 USD" if currency == "USD" else "🇳🇬 NGN"

    text = (
        f"<b>👤 Profile</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Username: @{user.username or 'N/A'}\n"
        f"💰 Balance: {balance_display}\n"
        f"🌍 Currency: {currency_flag}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=profile_keyboard(currency),
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== TOGGLE CURRENCY ======================
@router.callback_query(F.data == "toggle_currency")
async def toggle_currency(callback: CallbackQuery):
    telegram_id = callback.from_user.id

    try:
        async with AsyncSessionLocal() as db:
            user = await UserService.get_user_by_telegram_id(db, telegram_id)

            if not user:
                await callback.answer("❌ User not found.", show_alert=True)
                return

            # ✅ Toggle currency
            user.currency = "USD" if user.currency == "NGN" else "NGN"
            await db.commit()

        symbol = "🇺🇸 USD" if user.currency == "USD" else "🇳🇬 NGN"
        await callback.answer(f"Currency switched to {symbol}", show_alert=True)

        # ✅ Refresh profile with new currency
        await profile_menu(callback)

    except Exception as e:
        logger.error(f"toggle_currency failed: {e}")
        await callback.answer("❌ Failed to switch currency.", show_alert=True)
