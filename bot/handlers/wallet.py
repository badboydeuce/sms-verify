from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import httpx

from bot.states.wallet import (
    WalletStates
)

from core.config import settings

router = Router()


@router.message(
    WalletStates.enter_amount
)
async def process_funding_amount(
    message: Message,
    state: FSMContext
):

    try:

        amount = int(message.text)

    except ValueError:

        return await message.answer(
            "❌ Enter a valid amount"
        )

    if amount < 1500:

        return await message.answer(
            "❌ Minimum funding is ₦1,500"
        )

    await message.answer(
        "💳 Generating payment link..."
    )

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{settings.API_BASE_URL}/api/wallet/fund",
            json={
                "telegram_id":
                message.from_user.id,

                "amount":
                amount
            },
            timeout=30
        )

    data = response.json()

    if response.status_code != 200:

        return await message.answer(
            f"❌ {data.get('detail', 'Funding failed')}"
        )

    payment_url = data["authorization_url"]

    await message.answer(
        f"💳 Fund Wallet\n\n"
        f"Amount: ₦{amount:,}\n\n"
        f"Complete payment below:\n"
        f"{payment_url}"
    )

    await state.clear()