from aiogram import Router, types, F
from app.core.database import get_user, create_user

router = Router()


@router.message(F.text.lower() == "👤 my profile")
async def my_profile(message: types.Message):
    print("✅ PROFILE HANDLER TRIGGERED")

    telegram_id = str(message.from_user.id)

    user = get_user(telegram_id)

    if not user:
        user = create_user(telegram_id)

    balance = float(user["balance"]) if user and user["balance"] else 0

    text = f"""
👤 <b>My Profile</b>

🆔 ID: <code>{telegram_id}</code>
💰 Balance: ₦{balance:.2f}
📦 Active Numbers: 0
📊 Total Orders: 0
"""

    await message.answer(text)
