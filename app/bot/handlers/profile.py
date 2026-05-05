from aiogram import Router, types, F

from app.services.user_service import UserService

router = Router()
user_service = UserService()


# =========================
# 👤 PROFILE
# =========================
@router.message(F.text == "👤 My Profile")
async def my_profile(message: types.Message):

    telegram_id = str(message.from_user.id)

    balance = user_service.get_balance(telegram_id)
    total = user_service.get_total_purchases(telegram_id)
    active = user_service.get_active_numbers(telegram_id)

    text = (
        f"👤 *My Profile*\n\n"
        f"🆔 Telegram ID: `{telegram_id}`\n"
        f"💰 Balance: {balance}\n"
        f"📦 Total Purchases: {total}\n"
        f"📱 Active Numbers: {active}"
    )

    await message.answer(text, parse_mode="Markdown")
