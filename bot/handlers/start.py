# bot/handlers/start.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_user, create_user

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    user = await get_user(user_id)

    if not user:
        await create_user(
            telegram_id=user_id,
            username=username
        )

    kb = InlineKeyboardBuilder()

    kb.button(text="🛒 Buy Number", callback_data="buy_number")
    kb.button(text="📦 My Orders", callback_data="my_orders")
    kb.button(text="💰 Balance", callback_data="balance")
    kb.button(text="➕ Deposit", callback_data="deposit")
    kb.button(text="📞 Rent Number", callback_data="rent_number")
    kb.button(text="👤 Profile", callback_data="profile")
    kb.button(text="🆘 Support", callback_data="support")

    kb.adjust(2)

    text = f"""
👋 Welcome to <b>DeuceVerify</b>

Your trusted SMS verification platform.

━━━━━━━━━━━━━━
⚡ Instant SMS Codes
🌍 Worldwide Numbers
🔒 Secure & Fast
💰 Affordable Pricing
━━━━━━━━━━━━━━

Use the menu below to continue.
"""

    await message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data == "profile")
async def profile_handler(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)

    balance = user["balance"]

    text = f"""
👤 <b>Your Profile</b>

🆔 ID: <code>{callback.from_user.id}</code>
💰 Balance: ₦{balance}
📛 Username: @{callback.from_user.username or "None"}

Thank you for using DeuceVerify.
"""

    await callback.message.edit_text(text=text)
    await callback.answer()


@router.callback_query(F.data == "balance")
async def balance_handler(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)

    await callback.message.answer(
        f"💰 Your current balance is: ₦{user['balance']}"
    )

    await callback.answer()


@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    await callback.message.answer(
        "🆘 Support: @DeuceVerifySupport"
    )

    await callback.answer()


@router.callback_query(F.data == "buy_number")
async def buy_number_handler(callback: CallbackQuery):
    await callback.message.answer(
        "📲 Select a service to purchase a number."
    )

    await callback.answer()


@router.callback_query(F.data == "deposit")
async def deposit_handler(callback: CallbackQuery):
    await callback.message.answer(
        """
💳 Deposit Funds

Supported:
• Paystack
• Crypto (Coming Soon)

Send payment proof to support if needed.
"""
    )

    await callback.answer()


@router.callback_query(F.data == "rent_number")
async def rent_number_handler(callback: CallbackQuery):
    await callback.message.answer(
        "📞 Rental numbers feature coming soon."
    )

    await callback.answer()


@router.callback_query(F.data == "my_orders")
async def orders_handler(callback: CallbackQuery):
    await callback.message.answer(
        "📦 You currently have no active orders."
    )

    await callback.answer()