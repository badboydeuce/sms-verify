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

from bot.keyboards.buy import (
    buy_menu_keyboard,
    rental_duration_keyboard,
    rental_countries_keyboard
)
from bot.keyboards.countries import countries_keyboard
from bot.keyboards.services import services_keyboard
from bot.keyboards.orders import activation_order_keyboard, rental_order_keyboard

from core.database.session import AsyncSessionLocal
from core.services.smsman_service import SMSManService
from core.services.fivesim_service import FiveSimService
from core.services.order_service import OrderService
from core.exceptions.wallet import InsufficientBalance
from core.exceptions.smsman import NumberUnavailable, SMSManAPIError
from core.utils.currency import format_amount

from workers.otp_poller import poll_order
from workers.rental_monitor import monitor_rental

logger = logging.getLogger(__name__)

router = Router()


# ====================== BUY MENU ======================
@router.callback_query(F.data == "buy_menu")
async def buy_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📱 Buy Number</b>\n\nChoose service type:\n\n"
        "• One-Time SMS\n• Rent Number",
        reply_markup=buy_menu_keyboard(),
        parse_mode="HTML"
    )
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
            await callback.message.edit_text(
                "♻️ <b>Rent a Number</b>\n\nSelect rental duration:",
                reply_markup=rental_duration_keyboard(),
                parse_mode="HTML"
            )

        elif service_type == "compatible":
            await callback.message.edit_text("⏳ Fetching countries from 5sim...")
            countries = await FiveSimService.get_countries()

            kb = InlineKeyboardBuilder()
            for country in countries[:40]:
                kb.button(
                    text=country["title"],
                    callback_data=BuyCallback(
                        action="5sim_country",
                        value=country["name"]
                    ).pack()
                )
            kb.button(
                text="🔍 Search Country",
                callback_data=BuyCallback(
                    action="5sim_search_country",
                    value="start"
                ).pack()
            )
            kb.button(text="🔙 Back", callback_data="buy_menu")
            kb.adjust(2)

            await callback.message.edit_text(
                "🌍 <b>5sim — Select Country</b>\n\nChoose a country:",
                reply_markup=kb.as_markup(),
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"choose_type failed: {e}")
        await callback.message.edit_text("⚠️ Failed to load options.")
    finally:
        await callback.answer()


# ====================== RENTAL DURATION SELECTED ======================
@router.callback_query(BuyCallback.filter(F.action == "rental_duration"))
async def choose_rental_duration(
    callback: CallbackQuery,
    callback_data: BuyCallback
):
    try:
        rent_type, time_str = callback_data.value.split("_")
        time = int(time_str)
    except ValueError:
        return await callback.answer("Invalid selection", show_alert=True)

    await callback.message.edit_text("⏳ Fetching available countries...")

    try:
        rental_countries = await SMSManService.get_rental_countries(rent_type, time)

        if not rental_countries:
            await callback.message.edit_text(
                "❌ No countries available for this duration.\n"
                "Try a different rental period."
            )
            return

        all_countries = await SMSManService.get_countries()
        country_map = {str(c["id"]): c["title"] for c in all_countries.values()}

        await callback.message.edit_text(
            f"🌍 <b>Select Country</b>\n\n"
            f"Rental: {time} {rent_type} — {len(rental_countries)} countries available",
            reply_markup=rental_countries_keyboard(
                rental_countries,
                country_map,
                rent_type,
                time
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"choose_rental_duration failed: {e}")
        await callback.message.edit_text("⚠️ Failed to fetch rental countries.")
    finally:
        await callback.answer()


# ====================== RENTAL COUNTRY SELECTED ======================
@router.callback_query(BuyCallback.filter(F.action == "rental_country"))
async def choose_rental_country(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    db_user
):
    try:
        parts = callback_data.value.split("|")
        country_id = parts[0]
        rent_type = parts[1]
        time = int(parts[2])
        price_ngn = Decimal(parts[3])
    except (ValueError, IndexError):
        return await callback.answer("Invalid selection", show_alert=True)

    processing = await callback.message.edit_text("⏳ Purchasing rental number...")

    try:
        all_countries = await SMSManService.get_countries()
        country_name = next(
            (c["title"] for c in all_countries.values()
             if str(c["id"]) == str(country_id)),
            "Unknown"
        )

        async with AsyncSessionLocal() as db:
            order = await OrderService.create_rental_order(
                db=db,
                user_id=db_user.id,
                country_id=country_id,
                country_name=country_name,
                rent_type=rent_type,
                time=time,
                price=price_ngn
            )

        await processing.edit_text(
            f"<b>✅ Rental Number Purchased</b>\n\n"
            f"📱 Number: <code>{order.number}</code>\n\n"
            f"🌍 Country: {order.country_name}\n\n"
            f"⏱ Duration: {order.rental_duration}\n\n"
            f"💰 Cost: {format_amount(float(order.cost), db_user.currency)}\n\n"
            f"⏳ Expires: {order.expires_at.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"Use the buttons below to check for incoming SMS.",
            reply_markup=rental_order_keyboard(order.id),
            parse_mode="HTML"
        )

        create_task(monitor_rental(
            bot=callback.bot,
            order_id=order.id,
            chat_id=callback.message.chat.id,
            message_id=processing.message_id
        ))

    except InsufficientBalance:
        await processing.edit_text(
            "❌ Insufficient balance.\n\nPlease fund your wallet first."
        )
    except SMSManAPIError as e:
        await processing.edit_text(f"⚠️ {str(e)}\n\nTry again.")
    except Exception as e:
        logger.exception(f"choose_rental_country failed: {e}")
        await processing.edit_text("❌ Purchase failed. Please try again.")
    finally:
        await callback.answer()


# ====================== CHOOSE COUNTRY (ACTIVATION) ======================
@router.callback_query(BuyCallback.filter(F.action == "country"))
async def choose_country(callback: CallbackQuery, callback_data: BuyCallback, db_user):
    country_id = callback_data.value
    await callback.message.edit_text("⏳ Fetching live prices...")

    try:
        services = await SMSManService.get_prices_with_markup(country_id)

        if not services:
            await callback.message.edit_text("❌ No services available in this country.")
            return

        await callback.message.edit_text(
            "📱 <b>Select Service</b>\n\nChoose a service to purchase.",
            reply_markup=services_keyboard(
                services, country_id, currency=db_user.currency
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"choose_country failed: {e}")
        await callback.message.edit_text("⚠️ Failed to fetch live prices. Try again.")
    finally:
        await callback.answer()


# ====================== 5SIM COUNTRY SELECTED ======================
@router.callback_query(BuyCallback.filter(F.action == "5sim_country"))
async def fivesim_country(callback: CallbackQuery, callback_data: BuyCallback, db_user):
    country = callback_data.value
    await callback.message.edit_text("⏳ Fetching available services...")

    try:
        products = await FiveSimService.get_products_with_markup(country)

        if not products:
            await callback.message.edit_text(
                "❌ No services available for this country."
            )
            return

        kb = InlineKeyboardBuilder()
        for p in products[:40]:
            price_display = format_amount(p["price_ngn"], db_user.currency)
            kb.button(
                text=f"{p['title']} — {price_display} ({p['qty']} left)",
                callback_data=BuyCallback(
                    action="5sim_service",
                    value=f"{country}|{p['name']}|{p['price_ngn']}"
                ).pack()
            )
        kb.button(
            text="🔍 Search Service",
            callback_data=BuyCallback(
                action="5sim_search_service",
                value=country
            ).pack()
        )
        kb.button(
            text="🔙 Back",
            callback_data=BuyCallback(action="type", value="compatible").pack()
        )
        kb.adjust(1)

        await callback.message.edit_text(
            f"📱 <b>5sim — Select Service</b>\n\nCountry: {country.title()}",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"fivesim_country failed: {e}")
        await callback.message.edit_text("⚠️ Failed to fetch services.")
    finally:
        await callback.answer()


# ====================== 5SIM SEARCH COUNTRY ======================
@router.callback_query(BuyCallback.filter(F.action == "5sim_search_country"))
async def fivesim_search_country_prompt(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(BuyStates.fivesim_search_country)
    await callback.message.edit_text(
        "🔍 <b>Search Country (5sim)</b>\n\nType the country name:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(BuyStates.fivesim_search_country)
async def fivesim_handle_country_search(message: Message, state: FSMContext):
    search_term = message.text.strip()

    try:
        countries = await FiveSimService.get_countries()
        filtered = [
            c for c in countries
            if search_term.lower() in c["title"].lower()
        ]

        if not filtered:
            await message.answer(
                f"❌ No countries found for <b>{search_term}</b>.\n\nTry a different keyword.",
                parse_mode="HTML"
            )
            return

        kb = InlineKeyboardBuilder()
        for country in filtered[:40]:
            kb.button(
                text=country["title"],
                callback_data=BuyCallback(
                    action="5sim_country",
                    value=country["name"]
                ).pack()
            )
        kb.button(
            text="🔙 Back",
            callback_data=BuyCallback(action="type", value="compatible").pack()
        )
        kb.adjust(2)

        await message.answer(
            f"🌍 <b>Results for:</b> <i>{search_term}</i>",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"fivesim_handle_country_search failed: {e}")
        await message.answer("⚠️ Search failed. Please try again.")
    finally:
        await state.clear()


# ====================== 5SIM SEARCH SERVICE ======================
@router.callback_query(BuyCallback.filter(F.action == "5sim_search_service"))
async def fivesim_search_service_prompt(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    state: FSMContext
):
    await state.update_data(fivesim_country=callback_data.value)
    await state.set_state(BuyStates.fivesim_search_service)
    await callback.message.edit_text(
        "🔍 <b>Search Service (5sim)</b>\n\nType the service name:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(BuyStates.fivesim_search_service)
async def fivesim_handle_service_search(message: Message, state: FSMContext, db_user):  # ✅
    search_term = message.text.strip()
    data = await state.get_data()
    country = data.get("fivesim_country")

    try:
        products = await FiveSimService.get_products_with_markup(country)
        filtered = [
            p for p in products
            if search_term.lower() in p["title"].lower()
        ]

        if not filtered:
            await message.answer(
                f"❌ No services found for <b>{search_term}</b>.\n\nTry a different keyword.",
                parse_mode="HTML"
            )
            return

        kb = InlineKeyboardBuilder()
        for p in filtered[:40]:
            price_display = format_amount(p["price_ngn"], db_user.currency)  # ✅
            kb.button(
                text=f"{p['title']} — {price_display} ({p['qty']} left)",
                callback_data=BuyCallback(
                    action="5sim_service",
                    value=f"{country}|{p['name']}|{p['price_ngn']}"
                ).pack()
            )
        kb.button(
            text="🔙 Back",
            callback_data=BuyCallback(
                action="5sim_country",
                value=country
            ).pack()
        )
        kb.adjust(1)

        await message.answer(
            f"📱 <b>Results for:</b> <i>{search_term}</i>",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"fivesim_handle_service_search failed: {e}")
        await message.answer("⚠️ Search failed. Please try again.")
    finally:
        await state.clear()


# ====================== 5SIM SERVICE SELECTED ======================
@router.callback_query(BuyCallback.filter(F.action == "5sim_service"))
async def fivesim_buy(callback: CallbackQuery, callback_data: BuyCallback, db_user):
    try:
        parts = callback_data.value.split("|")
        country = parts[0]
        product = parts[1]
        price_ngn = Decimal(parts[2])
    except (ValueError, IndexError):
        return await callback.answer("Invalid selection", show_alert=True)

    processing = await callback.message.edit_text("⏳ Purchasing number from 5sim...")

    try:
        async with AsyncSessionLocal() as db:
            from uuid import uuid4
            from sqlalchemy import update
            from core.services.wallet_service import WalletService

            reference = f"5sim_{uuid4()}"

            await WalletService.debit_balance(
                db=db,
                user_id=db_user.id,
                amount=price_ngn,
                reference=reference,
                description=f"{product.title()} via 5sim"
            )

            response = await FiveSimService.buy_activation(country, product)

            if "phone" not in response:
                await WalletService.credit_balance(
                    db=db,
                    user_id=db_user.id,
                    amount=price_ngn,
                    reference=f"refund_{reference}",
                    description=f"Refund: 5sim failed for {product.title()}"
                )
                await processing.edit_text("❌ Could not get number.")
                return

            order = await OrderService.create_activation_order(
                db=db,
                user_id=db_user.id,
                country_id=country,
                country_name=country.title(),
                service_id=str(response["id"]),
                service_name=product.title(),
                price=price_ngn,
                provider="5sim",
                chat_id=callback.message.chat.id,
                message_id=None
            )

        msg = await processing.edit_text(
            f"<b>✅ 5sim Number Purchased</b>\n\n"
            f"📱 Number: <code>{response['phone']}</code>\n\n"
            f"🌍 Country: {country.title()}\n\n"
            f"📦 Service: {product.title()}\n\n"
            f"💰 Cost: {format_amount(float(price_ngn), db_user.currency)}\n\n"
            f"⏳ Waiting for SMS...",
            parse_mode="HTML"
        )

        async with AsyncSessionLocal() as db2:
            from sqlalchemy import update
            from core.models.order import Order
            await db2.execute(
                update(Order)
                .where(Order.id == order.id)
                .values(message_id=msg.message_id)
            )
            await db2.commit()

        create_task(poll_fivesim_order(
            bot=callback.bot,
            fivesim_order_id=response["id"],
            chat_id=callback.message.chat.id,
            message_id=msg.message_id
        ))

    except InsufficientBalance:
        await processing.edit_text("❌ Insufficient balance. Fund your wallet.")
    except Exception as e:
        logger.exception(f"fivesim_buy failed: {e}")
        await processing.edit_text("❌ Purchase failed. Please try again.")
    finally:
        await callback.answer()


# ====================== 5SIM POLLER ======================
async def poll_fivesim_order(bot, fivesim_order_id, chat_id, message_id):
    import asyncio
    MAX_WAIT = 300
    INTERVAL = 5
    elapsed = 0

    while elapsed < MAX_WAIT:
        try:
            data = await FiveSimService.check_order(fivesim_order_id)
            status = data.get("status", "")
            sms_list = data.get("sms") or []

            if sms_list:
                sms = sms_list[-1]
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=(
                        f"✅ <b>SMS Received (5sim)</b>\n\n"
                        f"📱 Number: <code>{data['phone']}</code>\n"
                        f"📦 Service: {data['product'].title()}\n\n"
                        f"💬 Message:\n<code>{sms['text']}</code>"
                    ),
                    parse_mode="HTML"
                )
                await FiveSimService.finish_order(fivesim_order_id)
                return

            if status in ("CANCELED", "TIMEOUT", "BANNED", "FINISHED"):
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"⚠️ Order ended with status: {status}",
                    parse_mode="HTML"
                )
                return

        except Exception as e:
            logger.error(f"poll_fivesim_order error: {e}")

        await asyncio.sleep(INTERVAL)
        elapsed += INTERVAL

    try:
        await FiveSimService.cancel_order(fivesim_order_id)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=(
                "⏰ <b>No SMS Received (5sim)</b>\n\n"
                "Number expired after 5 minutes.\n"
                "Please try again."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"poll_fivesim_order timeout handler error: {e}")


# ====================== SEARCH COUNTRY (SMS-MAN) ======================
@router.callback_query(BuyCallback.filter(F.action == "search_country"))
async def search_country_prompt(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    state: FSMContext
):
    await state.set_state(BuyStates.search_country)
    await callback.message.edit_text(
        "🔍 <b>Search Country</b>\n\nType the country name:",
        parse_mode="HTML"
    )
    await callback.answer()


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


# ====================== SEARCH SERVICE (SMS-MAN) ======================
@router.callback_query(BuyCallback.filter(F.action == "search_service"))
async def search_service_prompt(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    state: FSMContext
):
    country_id = callback_data.value
    await state.update_data(country_id=country_id)
    await state.set_state(BuyStates.search_service)
    await callback.message.edit_text(
        "🔍 <b>Search Service</b>\n\nType the name of the service:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(BuyStates.search_service)
async def handle_search_input(message: Message, state: FSMContext, db_user):  # ✅
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
            reply_markup=services_keyboard(
                services, country_id,
                search=search_term,
                currency=db_user.currency  # ✅
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"handle_search_input failed: {e}")
        await message.answer("⚠️ Search failed. Please try again.")
    finally:
        await state.clear()


# ====================== BUY SERVICE (ACTIVATION) ======================
@router.callback_query(BuyCallback.filter(F.action == "service"))
async def buy_service(callback: CallbackQuery, callback_data: BuyCallback, db_user):
    try:
        country_id, service_id = callback_data.value.split("_")
    except ValueError:
        return await callback.answer("Invalid selection", show_alert=True)

    processing = await callback.message.edit_text("⏳ Processing your order...")

    try:
        services = await SMSManService.get_prices_with_markup(country_id)
        selected = next(
            (s for s in services if str(s["application_id"]) == str(service_id)),
            None
        )

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
            f"💰 Price: {format_amount(float(order.cost), db_user.currency)}\n\n"
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


# ====================== BACK TO MAIN MENU ======================
@router.callback_query(F.data == "main_menu")
async def back_main_menu(callback: CallbackQuery):
    from bot.keyboards.main_menu import main_menu_keyboard

    await callback.message.edit_text(
        "<b>🏠 Main Menu</b>\n\nWelcome to DeuceVerify",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
