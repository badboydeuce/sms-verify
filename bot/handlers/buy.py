# bot/handlers/buy.py
import logging
from decimal import Decimal
from asyncio import create_task

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories.buy import BuyCallback
from bot.states.buy import BuyStates

from bot.keyboards.buy import buy_menu_keyboard
from bot.keyboards.countries import countries_keyboard
from bot.keyboards.services import services_keyboard
from bot.keyboards.orders import activation_order_keyboard, rental_order_keyboard

from core.database.session import AsyncSessionLocal
from core.services.smsman_service import SMSManService
from core.services.order_service import OrderService
from core.exceptions.wallet import InsufficientBalance
from core.exceptions.smsman import NumberUnavailable, SMSManAPIError

from workers.otp_poller import poll_order
from workers.rental_monitor import monitor_rental

logger = logging.getLogger(__name__)

router = Router()


# ====================== BUY MENU ======================
@router.callback_query(F.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):
    text = """
<b>📱 Buy Number</b>

Choose service type:

- One-Time SMS
- Rent Number
"""
    await callback.message.edit_text(text=text, reply_markup=buy_menu_keyboard())
    await callback.answer()


# ====================== CHOOSE TYPE ======================
@router.callback_query(BuyCallback.filter(F.action == "type"))
async def choose_type(callback: CallbackQuery, callback_data: BuyCallback):
    service_type = callback_data.value

    try:
        if service_type == "activation":
            await callback.message.edit_text("⏳ Fetching countries...")
            countries = await SMSManService.get_countries()

            await callback.message.edit_text(
                "🌍 <b>Select Country</b>\n\nChoose country for activation number.",
                reply_markup=countries_keyboard(list(countries.values())),
                parse_mode="HTML"
            )

        elif service_type == "rental":
            await _show_rental_duration(callback)

    except Exception as e:
        logger.error(f"choose_type failed: {e}")
        await callback.message.edit_text("⚠️ Failed to load options.")
    finally:
        await callback.answer()


# ====================== RENTAL ======================
async def _show_rental_duration(callback: CallbackQuery):
    pass


# ====================== CHOOSE COUNTRY ======================
@router.callback_query(BuyCallback.filter(F.action == "country"))
async def choose_country(callback: CallbackQuery, callback_data: BuyCallback):
    country_id = callback_data.value
    await callback.message.edit_text("⏳ Fetching live prices...")

    try:
        services = await SMSManService.get_prices_with_markup(country_id)

        if not services:
            await callback.message.edit_text("❌ No services available in this country.")
            return

        await callback.message.edit_text(
            f"📱 <b>Select Service</b>\n\nCountry ID: {country_id}",
            reply_markup=services_keyboard(services, country_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"choose_country failed: {e}")
        await callback.message.edit_text("⚠️ Failed to fetch live prices. Try again.")
    finally:
        await callback.answer()


# ====================== SEARCH COUNTRY — PROMPT ======================
@router.callback_query(BuyCallback.filter(F.action == "search_country"))
async def search_country_prompt(callback: CallbackQuery, callback_data: BuyCallback, state: FSMContext):
    await state.set_state(BuyStates.search_country)
    await callback.message.edit_text(
        "🔍 <b>Search Country</b>\n\nType the country name:",
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== SEARCH COUNTRY — HANDLE INPUT ======================
@router.message(BuyStates.search_country)
async def handle_country_search_input(message: Message, state: FSMContext):
    search_term = message.text.strip()

    try:
        countries = await SMSManService.get_countries()
        country_list = list(countries.values())

        filtered = [
            c for c in country_list
            if search_term.lower() in c["title"].lower()
        ]

        if not filtered:
            await message.answer(
                f"❌ No countries found for <b>{search_term}</b>.\n\nTry a different keyword.",
                parse_mode="HTML"
            )
            return

        await message.answer(
            f"🌍 <b>Results for:</b> <i>{search_term}</i>",
            reply_markup=countries_keyboard(country_list, search=search_term),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"handle_country_search_input failed: {e}")
        await message.answer("⚠️ Search failed. Please try again.")
    finally:
        await state.clear()

# ====================== SEARCH SERVICE — PROMPT ======================
@router.callback_query(BuyCallback.filter(F.action == "search_service"))
async def search_service_prompt(callback: CallbackQuery, callback_data: BuyCallback, state: FSMContext):
    country_id = callback_data.value
    await state.update_data(country_id=country_id)
    await state.set_state(BuyStates.search_service)  # ✅ was BuyStates.searching_service
    await callback.message.edit_text(
        "🔍 <b>Search Service</b>\n\nType the name of the service you're looking for:",
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== SEARCH SERVICE — HANDLE INPUT ======================
@router.message(BuyStates.search_service)  # ✅ was BuyStates.searching_service
async def handle_search_input(message: Message, state: FSMContext):
    data = await state.get_data()
    country_id = data.get("country_id")
    search_term = message.text.strip()

    try:
        services = await SMSManService.get_prices_with_markup(country_id)
        filtered = [
            s for s in services
            if search_term.lower() in s["application"].lower()
        ]

        if not filtered:
            await message.answer(
                f"❌ No services found for <b>{search_term}</b>.\n\nTry a different keyword.",
                parse_mode="HTML"
            )
            return

        await message.answer(
            f"📱 <b>Results for:</b> <i>{search_term}</i>",
            reply_markup=services_keyboard(services, country_id, search=search_term),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"handle_search_input failed: {e}")
        await message.answer("⚠️ Search failed. Please try again.")
    finally:
        await state.clear()

# ====================== BUY SERVICE ======================
@router.callback_query(BuyCallback.filter(F.action == "service"))
async def buy_service(callback: CallbackQuery, callback_data: BuyCallback, db_user):
    try:
        country_id, service_id = callback_data.value.split("_")
    except ValueError:
        return await callback.answer("Invalid selection", show_alert=True)

    processing = await callback.message.edit_text("⏳ Processing your order...")

    try:
        services = await SMSManService.get_prices_with_markup(country_id)
        selected = next((s for s in services if str(s["application_id"]) == str(service_id)), None)

        if not selected:
            await processing.edit_text("❌ Service no longer available.")
            return

        final_price = Decimal(str(selected["price"]))

        countries = await SMSManService.get_countries()
        country_name = next(
            (c["title"] for c in countries.values() if str(c["id"]) == str(country_id)),
            "Unknown"
        )

        async with AsyncSessionLocal() as db:
            order = await OrderService.create_activation_order(
                db=db,
                user_id=db_user.id,
                country_id=country_id,
                country_name=country_name,
                service_id=service_id,
                service_name=selected["application"],
                price=final_price
            )

        msg = await processing.edit_text(
            f"<b>✅ Number Purchased Successfully</b>\n\n"
            f"📱 Number: <code>{order.number}</code>\n\n"
            f"🌍 Country: {order.country_name}\n\n"
            f"📦 Service: {order.service_name}\n\n"
            f"💰 Price: ₦{order.cost}\n\n"
            f"⏳ Waiting for SMS...",
            reply_markup=activation_order_keyboard(order.id),
            parse_mode="HTML"
        )

        create_task(poll_order(
            bot=callback.bot,
            order_id=order.id,
            chat_id=callback.message.chat.id,
            message_id=msg.message_id
        ))

    except InsufficientBalance:
        await processing.edit_text("❌ Insufficient balance. Fund your wallet.")
    except Exception as e:
        logger.exception("buy_service error")
        await processing.edit_text("❌ Purchase failed. Please try again.")
    finally:
        await callback.answer()