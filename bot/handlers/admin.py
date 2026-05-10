# bot/handlers/admin.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import httpx
import logging

from bot.handlers.filters.admin import AdminFilter
from bot.keyboards.admin import admin_keyboard
from core.config import API_BASE_URL

router = Router()
logger = logging.getLogger(__name__)


# ====================== ADMIN PANEL ======================
@router.message(Command("admin"), AdminFilter())
async def admin_panel(message: Message):
    await message.answer(
        "<b>🛠 Admin Panel</b>",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


# ====================== CREDIT USER ======================
@router.message(Command("credit"), AdminFilter())
async def credit_user(message: Message):
    parts = message.text.split()

    if len(parts) != 3:
        await message.answer(
            "Usage: /credit &lt;telegram_id&gt; &lt;amount&gt;\n"
            "Example: /credit 123456789 5000"
        )
        return

    try:
        telegram_id = int(parts[1])
        amount = float(parts[2])
    except ValueError:
        await message.answer("❌ Invalid telegram_id or amount.")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/admin/credit",
                json={
                    "telegram_id": telegram_id,
                    "amount": amount
                }
            )
            response.raise_for_status()
            data = response.json()

        await message.answer(
            f"✅ <b>User Credited</b>\n\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n"
            f"💰 Amount: ₦{amount:,.2f}\n"
            f"💳 New Balance: ₦{data['new_balance']:,.2f}",
            parse_mode="HTML"
        )

        # Notify user
        await message.bot.send_message(
            chat_id=telegram_id,
            text=(
                f"✅ <b>Wallet Credited</b>\n\n"
                f"₦{amount:,.2f} has been added to your wallet.\n"
                f"💳 New Balance: ₦{data['new_balance']:,.2f}"
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Credit user failed: {e}")
        await message.answer("❌ Failed to credit user. Please try again.")
