from aiogram import Router, types
from aiogram.filters import Text
from app.core.database import get_user, create_user

router = Router()

@router.message(Text(text="👤 My Profile"))
async def my_profile(message: types.Message):
    telegram_id = message.from_user.id

    user = await get_user(telegram_id)

    if not user:
        user = await create_user(telegram_id)

    text = f"""
👤 <b>My Profile</b>

🆔 ID: <code>{telegram_id}</code>
💰 Balance: ₦{user.balance:.2f}
📦 Active Numbers: {user.active_numbers}
📊 Total Orders: {user.total_orders}
"""

    await message.answer(text)
