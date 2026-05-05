from aiogram import Router, types, F

from app.bot.bridge import init_payment
from app.utils.helpers import format_naira

router = Router()

# simple state
funding_users = set()


# =========================
# ➕ START FUNDING
# =========================
@router.message(F.text == "➕ Fund Wallet")
async def fund_wallet(message: types.Message):

    user_id = message.from_user.id
    funding_users.add(user_id)

    await message.answer(
        "💳 Enter amount to fund:\n\n"
        "Example: 1000\n\n"
        "Minimum: ₦500"
    )


# =========================
# 💳 HANDLE AMOUNT INPUT (SAFE)
# =========================
@router.message(F.text)
async def handle_amount(message: types.Message):

    user_id = message.from_user.id

    # only process if user is in funding mode
    if user_id not in funding_users:
        return

    text = message.text.strip()

    # validate number
    if not text.isdigit():
        await message.answer("❌ Please enter a valid number")
        return

    amount = int(text)

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
        funding_users.discard(user_id)
        return

    link = res["authorization_url"]

    await message.answer(
        f"💳 Click below to complete payment:\n\n{link}"
    )

    # exit funding mode
    funding_users.discard(user_id)
