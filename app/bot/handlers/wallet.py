from aiogram import Router, types

from app.bot.bridge import get_balance, init_payment
from app.utils.helpers import format_naira

router = Router()

# simple state
funding_users = set()


# =========================
# 💰 PROFILE CHECK
# =========================
@router.message(F.text == "👤 My Profile")
async def my_profile(message: types.Message):

    data = await get_balance(message.from_user.id)
    balance = data.get("balance", 0)

    await message.answer(
        f"👤 *My Profile*\n\n"
        f"🆔 ID: `{message.from_user.id}`\n"
        f"💰 Balance: {format_naira(balance)}",
        parse_mode="Markdown"
    )


# =========================
# ➕ START FUNDING
# =========================
@router.message(lambda msg: msg.text == "➕ Fund Wallet")
async def fund_wallet(message: types.Message):

    funding_users.add(message.from_user.id)

    await message.answer(
        "💳 Enter amount to fund:\n\n"
        "Example: 1000\n\n"
        "Minimum: ₦500"
    )


# =========================
# 💳 HANDLE AMOUNT INPUT
# =========================
@router.message()
async def handle_amount(message: types.Message):

    user_id = message.from_user.id

    # only handle if user is in funding mode
    if user_id not in funding_users:
        return

    # validate input
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number")
        return

    amount = int(message.text)

    if amount < 500:
        await message.answer("❌ Minimum funding is ₦500")
        return

    # call API
    res = await init_payment(
        user_id=user_id,
        amount=amount,
        email=f"user{user_id}@deuce.com"
    )

    if not res.get("success"):
        await message.answer("❌ Payment initialization failed")
        return

    link = res["authorization_url"]

    await message.answer(
        f"💳 Click below to complete payment:\n\n{link}"
    )

    # exit funding mode
    funding_users.remove(user_id)
