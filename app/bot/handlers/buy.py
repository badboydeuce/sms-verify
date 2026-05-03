from aiogram import Router, types
import asyncio

from app.bot.client import get_countries, get_services, buy_number, check_otp
from app.bot.keyboards.buy import countries_kb, services_kb

router = Router()

# simple in-memory state
user_state = {}


# Step 1: Start
@router.message(lambda msg: msg.text == "🛒 Buy Number")
async def buy_start(message: types.Message):

    data = get_countries()

    countries = list(data.keys())[:5]  # limit for now

    user_state[message.from_user.id] = {}

    await message.answer(
        "🌍 Select country:",
        reply_markup=countries_kb(countries)
    )


# Step 2: Select country
@router.message(lambda msg: msg.from_user.id in user_state and "country" not in user_state[msg.from_user.id])
async def select_country(message: types.Message):

    user_state[message.from_user.id]["country"] = message.text

    services = get_services(message.text)
    service_list = list(services.keys())[:5]

    await message.answer(
        "📱 Select service:",
        reply_markup=services_kb(service_list)
    )


# Step 3: Select service + Buy
@router.message(lambda msg: msg.from_user.id in user_state and "service" not in user_state[msg.from_user.id])
async def select_service(message: types.Message):

    user_id = message.from_user.id
    user_state[user_id]["service"] = message.text

    country = user_state[user_id]["country"]
    service = user_state[user_id]["service"]

    res = buy_number(country, service, user_id)

    if "activation_id" not in res:
        await message.answer("❌ Failed to buy number")
        return

    activation_id = res["activation_id"]
    number = res["number"]

    await message.answer(f"📱 Number: {number}\n⏳ Waiting for OTP...")

    # Step 4: OTP polling
    for _ in range(30):
        await asyncio.sleep(5)

        otp_res = check_otp(activation_id)

        if otp_res["status"] == "received":
            await message.answer(f"✅ OTP: {otp_res['otp']}")
            return

        if otp_res["status"] == "expired":
            await message.answer("⌛ Number expired. Refund initiated.")
            return

    await message.answer("⚠️ Timeout. Try again.")