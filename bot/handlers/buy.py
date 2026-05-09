import logging
from decimal import Decimal
from asyncio import create_task

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.callback_factories.buy import BuyCallback

from bot.keyboards.buy import (
    buy_menu_keyboard
)

from bot.keyboards.countries import (
    countries_keyboard
)

from bot.keyboards.services import (
    services_keyboard
)

from bot.keyboards.orders import (
    activation_order_keyboard
)

from core.database.session import (
    AsyncSessionLocal
)

from core.services.smsman_service import (
    SMSManService
)

from core.services.order_service import (
    OrderService
)

from core.exceptions.wallet import (
    InsufficientBalance
)

from core.exceptions.smsman import (
    NumberUnavailable,
    SMSManAPIError
)

from workers.otp_poller import (
    poll_order
)

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(
    F.data == "buy_menu"
)
async def buy_menu(
    callback: CallbackQuery
):

    text = """
<b>📱 Buy Number</b>

Choose service type:

• One-Time SMS
• Rent Number
• Compatible API
"""

    await callback.message.edit_text(
        text=text,
        reply_markup=buy_menu_keyboard()
    )

    await callback.answer()


@router.callback_query(
    BuyCallback.filter(
        F.action == "type"
    )
)
async def choose_type(
    callback: CallbackQuery,
    callback_data: BuyCallback
):

    service_type = callback_data.value

    try:

        if service_type == "activation":

            await callback.message.edit_text(
                "⏳ Fetching countries..."
            )

            countries = await SMSManService.get_countries()

            if not countries:
                await callback.message.edit_text(
                    "❌ No countries available."
                )
                return

            await callback.message.edit_text(
                """
🌍 <b>Select Country</b>

Choose country for activation number.
""",
                reply_markup=countries_keyboard(
                    list(countries.values())
                )
            )

        elif service_type == "rental":

            await callback.message.edit_text(
                """
♻️ Rental numbers coming next...

Choose:
• Hour
• Day
• Week
• Month
"""
            )

        elif service_type == "compatible":

            await callback.message.edit_text(
                """
🔗 Compatible API

API integration panel coming soon.
"""
            )

    except Exception as e:

        logger.error(f"choose_type failed: {e}")

        await callback.message.edit_text(
            "⚠️ Failed to fetch countries."
        )

    finally:

        await callback.answer()


@router.callback_query(
    BuyCallback.filter(
        F.action == "country"
    )
)
async def choose_country(
    callback: CallbackQuery,
    callback_data: BuyCallback
):

    country_id = callback_data.value

    await callback.message.edit_text(
        "⏳ Fetching available services..."
    )

    try:

        prices = await SMSManService.get_prices(country_id)

        if not prices:
            await callback.message.edit_text(
                "❌ No services available."
            )
            return

        services = []

        for item in prices:

            try:

                base_price = Decimal(str(item["price"]))

                final_price = Decimal(
                    str(SMSManService.apply_markup(float(base_price)))
                )

                services.append({
                    "id": item["application_id"],
                    "name": item["application"],
                    "price": final_price
                })

            except Exception as e:

                logger.warning(f"Skipping service item: {e}")
                continue

        if not services:
            await callback.message.edit_text(
                "❌ No purchasable services found."
            )
            return

        await callback.message.edit_text(
            """
📱 <b>Select Service</b>

Choose service to purchase.
""",
            reply_markup=services_keyboard(services, country_id)
        )

    except Exception as e:

        logger.error(f"choose_country failed: {e}")

        await callback.message.edit_text(
            "⚠️ Failed to fetch services."
        )

    finally:

        await callback.answer()


@router.callback_query(
    BuyCallback.filter(
        F.action == "service"
    )
)
async def buy_service(
    callback: CallbackQuery,
    callback_data: BuyCallback,
    db_user
):

    try:
        country_id, service_id = callback_data.value.split("_")
    except ValueError:
        return await callback.answer(
            "Invalid selection",
            show_alert=True
        )

    processing_message = await callback.message.edit_text(
        """
⏳ <b>Processing Order...</b>

Please wait while we purchase
your virtual number.
"""
    )

    try:

        prices = await SMSManService.get_prices(country_id)

        selected_service = next(
            (
                i for i in prices
                if str(i["application_id"]) == str(service_id)
            ),
            None
        )

        if not selected_service:
            await processing_message.edit_text(
                "❌ Service unavailable."
            )
            return

        base_price = Decimal(str(selected_service["price"]))

        final_price = Decimal(
            str(SMSManService.apply_markup(float(base_price)))
        )

        countries = await SMSManService.get_countries()

        country_name = next(
            (
                c["title"] for c in countries.values()
                if str(c["id"]) == str(country_id)
            ),
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
            f"""
<b>✅ Number Purchased</b>

📱 Number:
<code>{order.number}</code>

🌍 Country:
{order.country_name}

📦 Service:
{order.service_name}

💰 Cost:
₦{order.cost}

⏳ Waiting for SMS...

Auto-refresh every 5 seconds.
""",
            reply_markup=activation_order_keyboard(order.id)
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
            """
❌ Insufficient balance.

Please fund your wallet first.
"""
        )

    except NumberUnavailable:

        await processing_message.edit_text(
            """
🚫 Number not available.

Try another country or service.
"""
        )

    except SMSManAPIError:

        await processing_message.edit_text(
            """
⚠️ SMS-Man API error.

Retry again in a few seconds.
"""
        )

    except Exception as e:

        logger.error(f"buy_service failed: {e}")

        await processing_message.edit_text(
            f"""
❌ Purchase failed.

Error:
<code>{str(e)}</code>
"""
        )

    finally:

        await callback.answer()


@router.callback_query(
    F.data == "main_menu"
)
async def back_main_menu(
    callback: CallbackQuery
):

    from bot.keyboards.main_menu import (
        main_menu_keyboard
    )

    await callback.message.edit_text(
        """
<b>🏠 Main Menu</b>

Welcome to DeuceVerify
""",
        reply_markup=main_menu_keyboard()
    )

    await callback.answer()
