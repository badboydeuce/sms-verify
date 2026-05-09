from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

import httpx
import logging

from bot.states.wallet import WalletStates
from bot.keyboards.wallet import wallet_keyboard      # ← This was missing
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
        print("✅ Wallet menu sent successfully")
    except Exception as e:
        print(f"❌ Failed to send wallet menu: {e}")
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