from decimal import Decimal
from asyncio import create_task

from aiogram import Router, F
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

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

    if service_type == "activation":

        await callback.message.edit_text(
            "⏳ Fetching countries..."
        )

        try:

            countries = (
                await SMSManService.get_countries()
            )

            if not countries:

                return await callback.message.edit_text(
                    "❌ No countries available."
                )

            await callback.message.edit_text(
                """
🌍 <b>Select Country</b>

Choose country for activation number.
""",
                reply_markup=countries_keyboard(
                    countries
                )
            )

        except Exception:

            await callback.message.edit_text(
                "⚠️ Failed to fetch countries."
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

        prices = (
            await SMSManService.get_prices(
                country_id
            )
        )

        if not prices:

            return await callback.message.edit_text(
                "❌ No services available."
            )

        services = []

        for item in prices:

            try:

                base_price = Decimal(
                    str(item["price"])
                )

                final_price = Decimal(
                    str(
                        SMSManService.apply_markup(
                            float(base_price)
                        )
                    )
                )

                services.append({
                    "id":
                    item["application_id"],

                    "name":
                    item["application"],

                    "price":
                    final_price
                })

            except Exception:
                continue

        if not services:

            return await callback.message.edit_text(
                "❌ No purchasable services found."
            )

        await callback.message.edit_text(
            """
📱 <b>Select Service</b>

Choose service to purchase.
""",
            reply_markup=services_keyboard(
                services,
                country_id
            )
        )

    except Exception:

        await callback.message.edit_text(
            "⚠️ Failed to fetch services."
        )

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

        country_id, service_id = (
            callback_data.value.split(":")
        )

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

    async with AsyncSessionLocal() as db:

        try:

            prices = (
                await SMSManService.get_prices(
                    country_id
                )
            )

            selected_service = None

            for item in prices:

                if str(
                    item["application_id"]
                ) == str(service_id):

                    selected_service = item
                    break

            if not selected_service:

                return await processing_message.edit_text(
                    "❌ Service unavailable."
                )

            base_price = Decimal(
                str(selected_service["price"])
            )

            final_price = Decimal(
                str(
                    SMSManService.apply_markup(
                        float(base_price)
                    )
                )
            )

            order = (
                await OrderService.create_activation_order(
                    db=db,
                    user_id=db_user.id,
                    country_id=country_id,
                    country_name="Unknown",
                    service_id=service_id,
                    service_name=selected_service[
                        "application"
                    ],
                    price=final_price
                )
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
                reply_markup=activation_order_keyboard(
                    order.id
                )
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

            await processing_message.edit_text(
                f"""
❌ Purchase failed.

Error:
<code>{str(e)}</code>
"""
            )

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
