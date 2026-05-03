# app/bot/handlers/buy.py

import asyncio
from aiogram import Router, types

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
@router.message(lambda msg: msg.text == "🛒 Buy Number")
async def start_buy(message: types.Message):

    # ✅ FIX: await async call
    data = await get_countries()

    # handle empty response safely
    if not data:
        await message.answer("❌ Failed to load countries. Try again.")
        return

    countries = list(data.keys())[:5]

    user_state[message.from_user.id] = {}

    await message.answer(
        "🌍 Select country:",
        reply_markup=countries_kb(countries)
    )


# =========================
# 🌍 SELECT COUNTRY + SERVICE FLOW
# =========================
@router.message()
async def handle_steps(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_state:
        return

    state = user_state[user_id]

    # =========================
    # STEP 1: SELECT COUNTRY
    # =========================
    if "country" not in state:
        state["country"] = message.text

        # ✅ FIX: await async call
        services = await get_services(message.text)

        if not services:
            await message.answer("❌ Failed to load services.")
            return

        service_list = list(services.keys())[:5]

        await message.answer(
            "📱 Select service:",
            reply_markup=services_kb(service_list)
        )
        return

    # =========================
    # STEP 2: SELECT SERVICE + BUY
    # =========================
    if "service" not in state:
        state["service"] = message.text

        # ✅ FIX: await async call
        res = await buy_number(
            state["country"],
            state["service"],
            user_id
        )

        if not res.get("success"):
            await message.answer("❌ Failed to buy number")
            return

        request_id = res["request_id"]
        number = res["number"]

        await message.answer(f"📞 Number: {number}\n⏳ Waiting for OTP...")

        # =========================
        # 📩 OTP POLLING (TEMP SOLUTION)
        # =========================
        for _ in range(30):
            await asyncio.sleep(5)

            # ✅ FIX: await async call
            otp = await check_otp(request_id)

            if otp.get("status") == "received":
                await message.answer(f"✅ OTP: {otp['otp']}")

                # cleanup state after success
                user_state.pop(user_id, None)
                return

        await message.answer("⌛ Timeout. Try again.")

        # cleanup state on timeout
        user_state.pop(user_id, None)
