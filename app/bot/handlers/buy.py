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

user_state = {}


# =========================
# 🛒 START BUY FLOW
# =========================
@router.message(F.text)
async def start_buy(message: types.Message):

    if not message.text or "Buy Number" not in message.text:
        return

    countries = await get_countries()

    if not countries:
        await message.answer("❌ Failed to load countries. Try again.")
        return

    user_state[message.from_user.id] = {}

    await message.answer(
        "🌍 Select country:",
        reply_markup=countries_kb(countries)
    )


# =========================
# 🌍 STEP 1: COUNTRY SELECTED
# =========================
@router.message(F.text)
async def handle_country(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_state:
        return

    state = user_state[user_id]

    if "country" not in state:

        state["country"] = message.text

        services = await get_services()

        if not services:
            await message.answer("❌ Failed to load services.")
            return

        await message.answer(
            "📱 Select service:",
            reply_markup=services_kb(services)
        )
        return


# =========================
# 📱 STEP 2: SERVICE SELECTED → BUY
# =========================
@router.message(F.text)
async def handle_service(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_state:
        return

    state = user_state[user_id]

    if "country" in state and "service" not in state:

        state["service"] = message.text

        res = await buy_number(
            state["country"],
            state["service"],
            user_id
        )

        if not res.get("success"):
            await message.answer(
                f"❌ {res.get('error', 'Failed to buy number')}"
            )
            user_state.pop(user_id, None)
            return

        request_id = res["request_id"]
        number = res["number"]

        await message.answer(
            f"📞 Number: {number}\n⏳ Waiting for OTP..."
        )

        # =========================
        # 📩 OTP POLLING
        # =========================
        for _ in range(30):

            await asyncio.sleep(5)

            otp = await check_otp(request_id)

            if otp.get("status") == "received":

                await message.answer(f"✅ OTP: {otp['otp']}")

                user_state.pop(user_id, None)
                return

        await message.answer("⌛ Timeout. Try again.")
        user_state.pop(user_id, None)
