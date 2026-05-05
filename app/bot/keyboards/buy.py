# app/bot/handlers/buy.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.bridge import get_countries, get_services, buy_number
from app.bot.keyboards.buy import countries_kb, services_kb

router = Router()


# =========================
# 📦 STATES
# =========================
class BuyFlow(StatesGroup):
    country = State()
    service = State()


# =========================
# 🛒 START BUY FLOW
# =========================
@router.message(F.text == "🛒 Buy Number")
async def start_buy(message: types.Message, state: FSMContext):

    countries = await get_countries()

    if not countries:
        await message.answer("❌ No countries available at the moment.")
        return

    await state.set_state(BuyFlow.country)

    await message.answer(
        "🌍 Select Country:",
        reply_markup=countries_kb(countries)
    )


# =========================
# 🌍 COUNTRY SELECTION
# =========================
@router.message(BuyFlow.country)
async def select_country(message: types.Message, state: FSMContext):

    countries = await get_countries()
    valid_countries = [c["title"] for c in countries]

    if message.text not in valid_countries:
        await message.answer("❌ Please select a valid country from the menu.")
        return

    await state.update_data(country=message.text)

    services = await get_services(message.text)

    if not services:
        await message.answer("❌ No services available for this country.")
        await state.clear()
        return

    await state.set_state(BuyFlow.service)

    await message.answer(
        "📱 Select Service:",
        reply_markup=services_kb(services)
    )


# =========================
# 📱 SERVICE SELECTION + BUY
# =========================
@router.message(BuyFlow.service)
async def select_service(message: types.Message, state: FSMContext):

    data = await state.get_data()
    country = data.get("country")

    services = await get_services(country)
    valid_services = [s["name"] for s in services]

    if message.text not in valid_services:
        await message.answer("❌ Please select a valid service from the menu.")
        return

    result = await buy_number(
        country=country,
        service=message.text,
        user_id=message.from_user.id
    )

    await state.clear()

    if not result or not result.get("success"):
        await message.answer("❌ Purchase failed. Please try again.")
        return

    await message.answer(
        "📦 *Number Purchased Successfully*\n\n"
        f"📱 Number: `{result.get('number')}`\n"
        f"🆔 Request ID: `{result.get('request_id')}`\n\n"
        "⏳ Waiting for OTP...",
        parse_mode="Markdown"
    )


# =========================
# 🛡 GLOBAL FALLBACK (IMPORTANT)
# =========================
@router.message()
async def fallback(message: types.Message):
    await message.answer(
        "⚠️ Please use the menu buttons to navigate the system."
    )