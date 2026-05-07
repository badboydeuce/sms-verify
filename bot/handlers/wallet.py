from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message
)
from aiogram.fsm.context import FSMContext

from bot.states.wallet import (
    WalletStates
)

from bot.keyboards.wallet import (
    wallet_keyboard
)

router = Router()


@router.callback_query(
    F.data == "wallet_menu"
)
async def wallet_menu(
    callback: CallbackQuery,
    db_user
):

    text = f"""
<b>💰 Wallet</b>

Balance: ₦{db_user.balance}
"""

    await callback.message.edit_text(
        text,
        reply_markup=wallet_keyboard()
    )

    await callback.answer()


@router.callback_query(
    F.data.contains("wallet:fund")
)
async def fund_wallet_start(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        WalletStates.waiting_for_amount
    )

    await callback.message.edit_text(
        "💳 Enter funding amount:"
    )

    await callback.answer()


@router.message(
    WalletStates.waiting_for_amount
)
async def process_amount(
    message: Message,
    state: FSMContext
):

    amount = message.text

    await message.answer(
        f"Initializing ₦{amount} payment..."
    )

    await state.clear()
