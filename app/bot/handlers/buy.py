import asyncio
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.bot.states.buy import BuyFlow
from app.bot.bridge import get_countries, get_services, buy_number, check_otp
from app.bot.keyboards.buy import countries_kb, services_kb

router = Router()


# =========================
# 🛒 START FLOW
# =========================
@router.message(F.text == "🛒 Buy Number")
async def start_buy(message: types.Message, state: FSMContext):

    countries = await get_countries()

    if not countries:
        await message.answer("❌ Failed to load countries.")
        return

    await state.set_state(BuyFlow.country)

    await message.answer(
        "🌍 Select country:",
        reply_markup=countries_kb(countries)
    )


# =========================
# 🌍 COUNTRY STEP
# =========================
@router.message(BuyFlow.country)
async def select_country(message: types.Message, state: FSMContext):

    await state.update_data(country=message.text)

    services = await get_services()

    if not services:
        await message.answer("❌ Failed to load services.")
        return

    await state.set_state(BuyFlow.service)

    await message.answer(
        "📱 Select service:",
        reply_markup=services_kb(services)
    )


# =========================
# 📱 SERVICE STEP → BUY NUMBER
# =========================
@router.message(BuyFlow.service)
async def select_service(message: types.Message, state: FSMContext):

    data = await state.get_data()

    country = data["country"]
    service = message.text

    res = await buy_number(country, service, message.from_user.id)

    if not res.get("success"):
        await message.answer(f"❌ {res.get('error')}")
        await state.clear()
        return

    request_id = res["request_id"]

    await message.answer(
        f"📞 Number: {res['number']}\n⏳ Waiting for OTP..."
    )

    # =========================
    # OTP POLLING
    # =========================
    for _ in range(30):

        await asyncio.sleep(5)

        otp = await check_otp(request_id)

        if otp.get("status") == "received":
            await message.answer(f"✅ OTP: {otp['otp']}")
            await state.clear()
            return

    await message.answer("⌛ Timeout. Try again.")
    await state.clear()
