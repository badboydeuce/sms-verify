# bot/handlers/wallet.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import httpx
import logging

from bot.states.wallet import WalletStates
from bot.keyboards.wallet import wallet_keyboard
from bot.keyboards.payments import payment_keyboard
from bot.callback_factories.wallet import WalletCallback
from core.config import API_BASE_URL

router = Router()
logger = logging.getLogger(__name__)


# ====================== WALLET MENU ======================
@router.callback_query(F.data == "wallet_menu")
async def wallet_menu(callback: CallbackQuery):
    await callback.answer("💰 Opening Wallet...", show_alert=False)

    text = "💰 **Wallet Menu**\n\nChoose an option:"

    try:
        await callback.message.answer(
            text,
            reply_markup=wallet_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send wallet menu: {e}")
        await callback.answer("Failed to open menu", show_alert=True)


# ====================== FUND WALLET ======================
@router.callback_query(WalletCallback.filter(F.action == "fund"))
async def fund_wallet_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.message.answer(
        "💳 **Fund Your Wallet**\n\n"
        "Please enter the amount you want to fund:\n"
        "• Minimum: ₦1,500\n\n"
        "Send /cancel at any time to cancel this process.",
        parse_mode="Markdown"
    )

    await state.set_state(WalletStates.enter_amount)
    await callback.answer()


# ====================== PROCESS AMOUNT ======================
@router.message(WalletStates.enter_amount)
async def process_fund_amount(
    message: Message,
    state: FSMContext
):
    raw = message.text.strip()

    # Handle /cancel
    if raw == "/cancel":
        await state.clear()
        await message.answer("❌ Funding cancelled.")
        return

    # Validate input is a number
    try:
        amount = float(raw)
    except ValueError:
        await message.answer(
            "⚠️ Invalid amount. Please enter a number e.g. *2000*",
            parse_mode="Markdown"
        )
        return

    # Validate minimum
    if amount < 1500:
        await message.answer(
            "⚠️ Minimum funding amount is ₦1,500. Please enter a higher amount."
        )
        return

    await state.clear()

    telegram_id = message.from_user.id

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/wallet/fund",
                json={
                    "telegram_id": telegram_id,
                    "amount": amount
                }
            )
            response.raise_for_status()
            data = response.json()

        await message.answer(
            f"✅ **Payment Link Generated**\n\n"
            f"Click the link below to complete your payment:\n"
            f"{data['authorization_url']}\n\n"
            f"Reference: `{data['reference']}`",
            parse_mode="Markdown"
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Fund wallet API error: {e}")
        await message.answer(
            "❌ Failed to generate payment link. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error funding wallet: {e}")
        await message.answer(
            "❌ Something went wrong. Please try again later."
        )
