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
from bot.keyboards.orders import activation_order_keyboard

from core.database.session import AsyncSessionLocal
from core.services.smsman_service import SMSManService
from core.services.order_service import OrderService
from core.exceptions.wallet import InsufficientBalance
from core.exceptions.smsman import NumberUnavailable, SMSManAPIError
from workers.otp_poller import poll_order

logger = logging.getLogger(__name__)

router = Router()


# ====================== BUY MENU ======================
@router.callback_query(F.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):
    text = """
<b>📱 Buy Number</b>

Choose service type:

• One-Time SMS
• Rent Number
• Compatible API
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

            if not countries:
                await callback.message.edit_text("❌ No countries available.")
                return

            await callback.message.edit_text(
                "🌍 <b>Select Country</b>\n\nChoose country for activation number.",
                reply_markup=countries_keyboard(list(countries.values())),
                parse_mode="HTML"
            )

        elif service_type == "rental":
            await _show_rental_duration(callback)

        elif service_type == "compatible":
            await callback.message.edit_text(
                "🔗 Compatible API\n\nAPI integration panel coming soon."
            )

    except Exception as e:
        logger.error(f"choose_type failed: {e}")
        await callback.message.edit_text("⚠️ Failed to load options.")

    finally:
        await callback.answer()


# ====================== RENTAL DURATION ======================
async def _show_rental_duration(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()

    durations = [
        ("1 Hour", "hour_1"),
        ("4 Hours", "hour_4"),
        ("1 Day", "day_1"),
        ("1 Week", "week_1"),
        ("1 Month", "month_1"),
    ]

    for label, value in durations:
        kb.button(
            text=label,
            callback_data=BuyCallback(action="rental_duration", value=value).pack()
        )

    kb.button(
        text="🔙 Back",
        callback_data=BuyCallback(action="type", value="activation").pack()
    )

    kb.adjust(2)

    await callback.message.edit_text(
        "♻️ <b>Rent Number</b>\n\nSelect rental duration:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


# ====================== RENTAL DURATION SELECTED ======================
@router.callback_query(BuyCallback.filter(F.action == "rental_duration"))
async def rental_duration_selected(
    callback: CallbackQuery,
    callback_data: BuyCallback
):
    duration = callback_data.value
    rent_type, time_str = duration.rsplit("_", 1)
    time = int(time_str)

    await callback.message.edit_text("⏳ Fetching available countries...")

    try:
        # ✅ Call limits with no country_id to get all available countries
        limits_data = await SMSManService.get_rental_limits(
            country_id="",
            rent_type=rent_type,
            time=time
        )

        print(f"RENTAL LIMITS ALL: {limits_data}", flush=True)

        if not limits_data or "error_code" in limits_data:
            await callback.message.edit_text("❌ No rental countries available.")
            return

        # ✅ Filter only countries with count > 0
        available = [
            l for l in limits_data.get("limits", [])
            if int(l.get("count", 0)) > 0
        ]

        if not available:
            await callback.message.edit_text(
                "❌ No rental numbers available for this duration."
            )
            return

        # Get country names
        countries = await SMSManService.get_countries()

        kb = InlineKeyboardBuilder()

        for limit in available:
            cid = str(limit["country_id"])
            country = countries.get(cid)
            name = country["title"] if country else f"Country {cid}"
            cost = Decimal(str(SMSManService.apply_rental_markup(float(limit["cost"]))))

            kb.button(
                text=f"{name} — ₦{cost}",
                callback_data=BuyCallback(
                    action="rental_country",
                    value=f"{cid}_{duration}"
                ).pack()
            )

        kb.button(
            text="🔙 Back",
            callback_data=BuyCallback(action="type", value="rental").pack()
        )

        kb.adjust(1)

        await callback.message.edit_text(
            f"🌍 <b>Available Countries</b>\n\nShowing countries with rental numbers for your selected duration.",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"rental_duration_selected failed: {e}")
        await callback.message.edit_text("⚠️ Failed to fetch countries.")

    finally:
        await callback.answer()

# ====================== RENTAL SEARCH COUNTRY ======================
@router.callback_query(BuyCallback.filter(F.action == "rental_search_country"))
async def rental_search_country_start(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    state: FSMContext
):
    await state.update_data(duration=callback_data.value)
    await callback.message.answer(
        "🔍 Type the country name to search:\nSend /cancel to go back."
    )
    await state.set_state(BuyStates.rental_search_country)
    await callback.answer()


@router.message(BuyStates.rental_search_country)
async def rental_search_country_result(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Search cancelled.")
        return

    search = message.text.strip()
    data = await state.get_data()
    duration = data.get("duration")
    await state.clear()

    countries = await SMSManService.get_countries()
    filtered = [
        c for c in countries.values()
        if search.lower() in c["title"].lower()
    ]

    if not filtered:
        await message.answer(
            f"❌ No countries found for <b>{search}</b>. Try again.",
            parse_mode="HTML"
        )
        return

    kb = InlineKeyboardBuilder()

    for country in filtered[:40]:
        kb.button(
            text=country["title"],
            callback_data=BuyCallback(
                action="rental_country",
                value=f"{country['id']}_{duration}"
            ).pack()
        )

    kb.adjust(2)

    await message.answer(
        f"🌍 <b>Results for \"{search}\":</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


# ====================== RENTAL COUNTRY SELECTED ======================
@router.callback_query(BuyCallback.filter(F.action == "rental_country"))
async def rental_country_selected(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    db_user
):
    parts = callback_data.value.split("_", 1)
    country_id = parts[0]
    duration = parts[1]

    rent_type, time_str = duration.rsplit("_", 1)
    time = int(time_str)

    processing_message = await callback.message.edit_text(
        "⏳ <b>Processing Rental...</b>\n\nPlease wait while we get your rental number.",
        parse_mode="HTML"
    )

    try:
        limits_data = await SMSManService.get_rental_limits(country_id, rent_type, time)

        if not limits_data or "error_code" in limits_data:
            await processing_message.edit_text(
                "❌ Rental unavailable for this country."
            )
            return

        limits_list = limits_data.get("limits", [])
        country_limit = next(
            (l for l in limits_list if str(l["country_id"]) == str(country_id)),
            None
        )

        if not country_limit or int(country_limit.get("count", 0)) == 0:
            await processing_message.edit_text(
                "❌ No rental numbers available for this country."
            )
            return

        countries = await SMSManService.get_countries()
        country_name = next(
            (c["title"] for c in countries.values() if str(c["id"]) == str(country_id)),
            "Unknown"
        )

        base_price = Decimal(str(country_limit["cost"]))
        final_price = Decimal(str(SMSManService.apply_rental_markup(float(base_price))))  # ✅

        async with AsyncSessionLocal() as db:
            order = await OrderService.create_rental_order(
                db=db,
                user_id=db_user.id,
                country_id=country_id,
                country_name=country_name,
                rent_type=rent_type,
                time=time,
                price=final_price
            )

        await processing_message.edit_text(
            f"<b>✅ Rental Number Purchased</b>\n\n"
            f"📱 Number:\n<code>{order.number}</code>\n\n"
            f"🌍 Country:\n{order.country_name}\n\n"
            f"⏱ Duration:\n{order.rental_duration}\n\n"
            f"💰 Cost:\n₦{order.cost}\n\n"
            f"📩 SMS will appear here as they arrive.",
            parse_mode="HTML"
        )

    except InsufficientBalance:
        await processing_message.edit_text(
            "❌ Insufficient balance.\n\nPlease fund your wallet first."
        )

    except Exception as e:
        logger.error(f"rental_country_selected failed: {e}")
        await processing_message.edit_text(
            "❌ Rental failed. Please try again."
        )

    finally:
        await callback.answer()


# ====================== SEARCH COUNTRY ======================
@router.callback_query(BuyCallback.filter(F.action == "search_country"))
async def search_country_start(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.message.answer(
        "🔍 Type the country name to search:\nSend /cancel to go back."
    )
    await state.set_state(BuyStates.search_country)
    await callback.answer()


@router.message(BuyStates.search_country)
async def search_country_result(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Search cancelled.")
        return

    search = message.text.strip()
    await state.clear()

    countries = await SMSManService.get_countries()
    filtered = [
        c for c in countries.values()
        if search.lower() in c["title"].lower()
    ]

    if not filtered:
        await message.answer(
            f"❌ No countries found for <b>{search}</b>. Try again.",
            parse_mode="HTML"
        )
        return

    await message.answer(
        f"🌍 <b>Results for \"{search}\":</b>",
        reply_markup=countries_keyboard(filtered),
        parse_mode="HTML"
    )


# ====================== CHOOSE COUNTRY ======================
@router.callback_query(BuyCallback.filter(F.action == "country"))
async def choose_country(callback: CallbackQuery, callback_data: BuyCallback):
    country_id = callback_data.value

    await callback.message.edit_text("⏳ Fetching available services...")

    try:
        prices = await SMSManService.get_prices(country_id)

        if not prices:
            await callback.message.edit_text("❌ No services available.")
            return

        services = []
        for item in prices:
            try:
                base_price = Decimal(str(item["price"]))
                final_price = Decimal(str(SMSManService.apply_markup(float(base_price))))
                services.append({
                    "id": item["application_id"],
                    "name": item["application"],
                    "price": final_price
                })
            except Exception as e:
                logger.warning(f"Skipping service item: {e}")
                continue

        if not services:
            await callback.message.edit_text("❌ No purchasable services found.")
            return

        await callback.message.edit_text(
            "📱 <b>Select Service</b>\n\nChoose service to purchase.",
            reply_markup=services_keyboard(services, country_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"choose_country failed: {e}")
        await callback.message.edit_text("⚠️ Failed to fetch services.")

    finally:
        await callback.answer()


# ====================== SEARCH SERVICE ======================
@router.callback_query(BuyCallback.filter(F.action == "search_service"))
async def search_service_start(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    state: FSMContext
):
    await state.update_data(country_id=callback_data.value)
    await callback.message.answer(
        "🔍 Type the service name to search:\nSend /cancel to go back."
    )
    await state.set_state(BuyStates.search_service)
    await callback.answer()


@router.message(BuyStates.search_service)
async def search_service_result(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Search cancelled.")
        return

    search = message.text.strip()
    data = await state.get_data()
    country_id = data.get("country_id")
    await state.clear()

    prices = await SMSManService.get_prices(country_id)
    filtered = [
        s for s in prices
        if search.lower() in s["application"].lower()
    ]

    if not filtered:
        await message.answer(
            f"❌ No services found for <b>{search}</b>. Try again.",
            parse_mode="HTML"
        )
        return

    services = [
        {
            "id": s["application_id"],
            "name": s["application"],
            "price": Decimal(str(SMSManService.apply_markup(float(s["price"]))))
        }
        for s in filtered
    ]

    await message.answer(
        f"📱 <b>Results for \"{search}\":</b>",
        reply_markup=services_keyboard(services, country_id),
        parse_mode="HTML"
    )


# ====================== BUY SERVICE ======================
@router.callback_query(BuyCallback.filter(F.action == "service"))
async def buy_service(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    db_user
):
    try:
        country_id, service_id = callback_data.value.split("_")
    except ValueError:
        return await callback.answer("Invalid selection", show_alert=True)

    processing_message = await callback.message.edit_text(
        "⏳ <b>Processing Order...</b>\n\nPlease wait while we purchase your virtual number.",
        parse_mode="HTML"
    )

    try:
        prices = await SMSManService.get_prices(country_id)

        selected_service = next(
            (i for i in prices if str(i["application_id"]) == str(service_id)),
            None
        )

        if not selected_service:
            await processing_message.edit_text("❌ Service unavailable.")
            return

        base_price = Decimal(str(selected_service["price"]))
        final_price = Decimal(str(SMSManService.apply_markup(float(base_price))))

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
                service_name=selected_service["application"],
                price=final_price
            )

        msg = await processing_message.edit_text(
            f"<b>✅ Number Purchased</b>\n\n"
            f"📱 Number:\n<code>{order.number}</code>\n\n"
            f"🌍 Country:\n{order.country_name}\n\n"
            f"📦 Service:\n{order.service_name}\n\n"
            f"💰 Cost:\n₦{order.cost}\n\n"
            f"⏳ Waiting for SMS...\n\nAuto-refresh every 5 seconds.",
            reply_markup=activation_order_keyboard(order.id),
            parse_mode="HTML"
        )

        create_task(
            poll_order(
                bot=callback.bot,
                order_id=order.id,
                chat_id=callback.message.chat.id,
                message_id=msg.message_id
            )
        )

    except InsufficientBalance:
        await processing_message.edit_text(
            "❌ Insufficient balance.\n\nPlease fund your wallet first."
        )

    except NumberUnavailable:
        await processing_message.edit_text(
            "🚫 Number not available.\n\nTry another country or service."
        )

    except SMSManAPIError:
        await processing_message.edit_text(
            "⚠️ SMS-Man API error.\n\nRetry again in a few seconds."
        )

    except Exception as e:
        logger.error(f"buy_service failed: {e}")
        await processing_message.edit_text(
            "❌ Purchase failed. Please try again."
        )

    finally:
        await callback.answer()


# ====================== MAIN MENU ======================
@router.callback_query(F.data == "main_menu")
async def back_main_menu(callback: CallbackQuery):
    from bot.keyboards.main_menu import main_menu_keyboard

    await callback.message.edit_text(
        "<b>🏠 Main Menu</b>\n\nWelcome to DeuceVerify",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()
