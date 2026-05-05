import asyncio
from aiogram import Router, types, F

from app.bot.bridge import (
    get_countries,
    get_services,
    buy_number,
    check_otp
)

from app.bot.keyboards.buy import countries_kb, services_kb

router = Router()

# user_id → state
user_state = {}


# =========================
# 🛒 START BUY FLOW
# =========================
@router.message(F.text == "🛒 Buy Number")
async def start_buy(message: types.Message):

    countries = await get_countries()

    if not countries:
        await message.answer("❌ Failed to load countries.")
        return

    user_state[message.from_user.id] = {}

    await message.answer(
        "🌍 Select country:",
        reply_markup=countries_kb(countries)
    )


# =========================
# 🌍 COUNTRY SELECTED
# =========================
@router.callback_query(F.data.startswith("country:"))
async def select_country(call: types.CallbackQuery):

    country_id = call.data.split(":")[1]

    user_state[call.from_user.id] = {
        "country": country_id
    }

    services = await get_services()

    if not services:
        await call.message.answer("❌ Failed to load services.")
        return

    await call.message.answer(
        "📱 Select service:",
        reply_markup=services_kb(services)
    )

    await call.answer()


# =========================
# 📱 SERVICE SELECTED → BUY NUMBER
# =========================
@router.callback_query(F.data.startswith("service:"))
async def select_service(call: types.CallbackQuery):

    service_id = call.data.split(":")[1]
    user_id = call.from_user.id

    state = user_state.get(user_id, {})

    if "country" not in state:
        await call.message.answer("❌ Please select country first.")
        return

    state["service"] = service_id

    res = await buy_number(
        state["country"],
        state["service"],
        user_id
    )

    if not res.get("success"):
        await call.message.answer(
            f"❌ {res.get('error', 'Failed to buy number')}"
        )
        user_state.pop(user_id, None)
        return

    request_id = res["request_id"]
    number = res["number"]

    await call.message.answer(
        f"📞 Number: {number}\n⏳ Waiting for OTP..."
    )

    # =========================
    # 📩 OTP POLLING
    # =========================
    for _ in range(30):

        await asyncio.sleep(5)

        otp = await check_otp(request_id)

        if otp.get("status") == "received":

            await call.message.answer(f"✅ OTP: {otp['otp']}")

            user_state.pop(user_id, None)
            await call.answer()
            return

    await call.message.answer("⌛ Timeout. Try again.")

    user_state.pop(user_id, None)
    await call.answer()
