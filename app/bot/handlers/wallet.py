from aiogram import Router, types

from app.bot.bridge import get_balance
from app.utils.helpers import format_naira

router = Router()


# =========================
# 💰 CHECK BALANCE
# =========================
@router.message(lambda msg: msg.text == "💰 Balance")
async def check_balance(message: types.Message):

    data = await get_balance(message.from_user.id)

    balance = data.get("balance", 0)

    await message.answer(
        f"💰 Your Balance:\n\n{format_naira(balance)}"
    )


# =========================
# ➕ FUND WALLET
# =========================
@router.message(lambda msg: msg.text == "➕ Fund Wallet")
async def fund_wallet(message: types.Message):

    await message.answer(
        "💳 To fund your wallet:\n\n"
        "Send amount (e.g. 1000)\n\n"
        "Minimum: ₦500"
    )
