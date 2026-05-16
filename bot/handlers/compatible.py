# bot/handlers/compatible.py

import logging
from decimal import Decimal
from asyncio import create_task

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories.buy import BuyCallback
from core.database.session import AsyncSessionLocal
from core.services.fivesim_service import FiveSimService
from core.services.order_service import OrderService
from core.exceptions.wallet import InsufficientBalance
from core.exceptions.smsman import SMSManAPIError
from workers.otp_poller import poll_order

logger = logging.getLogger(__name__)
router = Router()


# ====================== COMPATIBLE MENU ======================
@router.callback_query(BuyCallback.filter(F.action == "type"), lambda c, d: d.value == "compatible")
async def compatible_menu(callback: CallbackQuery, callback_data: BuyCallback):
    await callback.message.edit_text("⏳ Fetching countries from 5sim...")

    try:
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
        kb.button(text="🔙 Back", callback_data="buy_menu")
        kb.adjust(2)

        await callback.message.edit_text(
            "🌍 <b>5sim — Select Country</b>\n\nChoose a country:",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"compatible_menu failed: {e}")
        await callback.message.edit_text("⚠️ Failed to load countries.")
    finally:
        await callback.answer()


# ====================== 5SIM COUNTRY SELECTED ======================
@router.callback_query(BuyCallback.filter(F.action == "5sim_country"))
async def fivesim_country(callback: CallbackQuery, callback_data: BuyCallback):
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
            kb.button(
                text=f"{p['title']} — ₦{p['price_ngn']:,.0f} ({p['qty']} left)",
                callback_data=BuyCallback(
                    action="5sim_service",
                    value=f"{country}|{p['name']}|{p['price_ngn']}"
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
        response = await FiveSimService.buy_activation(country, product)

        if response.get("status") == "no free phones" or "phone" not in response:
            await processing.edit_text(
                "❌ No numbers available.\n\nTry a different country or service."
            )
            return

        async with AsyncSessionLocal() as db:
            order = await OrderService.create_activation_order(
                db=db,
                user_id=db_user.id,
                country_id=country,
                country_name=country.title(),
                service_id=str(response["id"]),
                service_name=product.title(),
                price=price_ngn
            )

        msg = await processing.edit_text(
            f"<b>✅ 5sim Number Purchased</b>\n\n"
            f"📱 Number: <code>{response['phone']}</code>\n\n"
            f"🌍 Country: {country.title()}\n\n"
            f"📦 Service: {product.title()}\n\n"
            f"💰 Cost: ₦{price_ngn:,.2f}\n\n"
            f"⏳ Waiting for SMS...",
            parse_mode="HTML"
        )

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

    # Timeout
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
