from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

import httpx
import logging

from bot.states.wallet import WalletStates
from bot.keyboards.payments import payment_keyboard
from bot.callback_factories.wallet import WalletCallback
from core.config import API_BASE_URL

router = Router()
logger = logging.getLogger(__name__)


# ====================== WALLET MENU ======================

@router.callback_query(F.data == "wallet_menu")
async def wallet_menu(callback: CallbackQuery):
    await callback.answer("✅ Wallet menu opened", show_alert=False)
    
    try:
        await callback.message.edit_text(
            "💰 **Wallet Menu**",
            reply_markup=wallet_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        # Fallback if edit_text fails
        await callback.message.answer(
            "💰 **Wallet Menu**",
            reply_markup=wallet_keyboard(),
            parse_mode="Markdown"
        )
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


@router.message(WalletStates.enter_amount)
async def process_funding_amount(
    message: Message, 
    state: FSMContext
):
    if message.text and message.text.startswith("/"):
        await state.clear()
        await message.answer("✅ Funding process cancelled.")
        return

    try:
        amount = int(message.text.strip())
    except ValueError:
        return await message.answer("❌ Please enter a valid number.")

    if amount < 1500:
        return await message.answer("❌ Minimum funding amount is ₦1,500.")

    await message.answer("🔄 Generating secure payment link...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/wallet/fund",
                json={
                    "telegram_id": message.from_user.id,
                    "amount": amount
                }
            )

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", "Failed to process request")
            except:
                error_msg = "Server error"
            
            await state.clear()
            return await message.answer(f"❌ {error_msg}")

        data = response.json()
        payment_url = data.get("authorization_url")

        if not payment_url:
            await state.clear()
            return await message.answer("❌ Failed to generate payment link.")

        # Success
        await message.answer(
            f"💳 **Fund Wallet**\n\n"
            f"Amount: <b>₦{amount:,}</b>\n\n"
            "Click the button below to pay:",
            parse_mode="HTML"
        )

        await message.answer(
            "💳 Pay Now",
            reply_markup=payment_keyboard(payment_url)
        )

    except httpx.TimeoutException:
        await message.answer("❌ Request timed out. Please try again.")
    except Exception as e:
        logger.error(f"Funding error: {e}")
        await message.answer("❌ Failed to connect to payment service.")
    finally:
        await state.clear()


# ====================== GLOBAL CANCEL ======================

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    if await state.get_state() is None:
        return await message.answer("✅ No active process.")

    await state.clear()
    await message.answer("✅ Process cancelled successfully.")