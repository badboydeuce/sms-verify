from decimal import Decimal

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message
)
from aiogram.fsm.context import FSMContext

from core.database.session import (
    AsyncSessionLocal
)

from core.services.paystack_service import (
    PaystackService
)

from core.models.payment_transaction import (
    PaymentTransaction
)

from core.validators.amount import (
    validate_funding_amount
)

from bot.states.wallet import (
    WalletStates
)

from bot.keyboards.wallet import (
    wallet_keyboard
)

from bot.keyboards.payments import (
    payment_keyboard
)

from core.utils.reference import (
    generate_reference
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
async def fund_wallet(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        WalletStates.waiting_for_amount
    )

    await callback.message.edit_text(
        """
💳 Enter amount to fund

Minimum: ₦1,500
"""
    )

    await callback.answer()


@router.message(
    WalletStates.waiting_for_amount
)
async def process_amount(
    message: Message,
    state: FSMContext,
    db_user
):

    try:

        amount = Decimal(
            message.text
        )

        validate_funding_amount(
            amount
        )

    except Exception as e:

        return await message.answer(
            f"❌ {str(e)}"
        )

    reference = generate_reference()

    async with AsyncSessionLocal() as db:

        payment = PaymentTransaction(
            user_id=db_user.id,
            reference=reference,
            amount=amount,
            status="pending"
        )

        db.add(payment)

        await db.commit()

    response = (
        await PaystackService.initialize_transaction(
            email=f"{db_user.telegram_id}@deuceverify.com",

            amount=int(amount * 100),

            reference=reference,

            metadata={
                "telegram_id":
                db_user.telegram_id,

                "user_id":
                db_user.id
            }
        )
    )

    payment_url = (
        response["data"]["authorization_url"]
    )

    await message.answer(
        f"""
<b>💳 Payment Ready</b>

Amount: ₦{amount}

Click below to complete payment.
""",
        reply_markup=payment_keyboard(
            payment_url
        )
    )

    await state.clear()
