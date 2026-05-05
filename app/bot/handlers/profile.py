from aiogram import Router, types, F
from app.core.database import get_user, create_user

router = Router()


@router.message(F.text.lower() == "👤 my profile")
async def my_profile(message: types.Message):
    print("✅ PROFILE HANDLER TRIGGERED")

    telegram_id = message.from_user.id

    user = await get_user(telegram_id)

    if not user:
        user = await create_user(telegram_id)

    # SAFE values (avoid None crash)
    balance = user.balance or 0
    active_numbers = user.active_numbers or 0
    total_orders = user.total_orders or 0

    text = f"""
👤 <b>My Profile</b>

🆔 ID: <code>{telegram_id}</code>
💰 Balance: ₦{balance:.2f}
📦 Active Numbers: {active_numbers}
📊 Total Orders: {total_orders}
"""

    await message.answer(text)
