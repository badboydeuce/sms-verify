# bot/handlers/orders.py

import logging
from asyncio import create_task
from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from bot.callback_factories.orders import OrderCallback
from bot.keyboards.orders import activation_order_keyboard, rental_order_keyboard
from core.database.session import AsyncSessionLocal
from core.models.order import Order
from core.services.order_service import OrderService
from core.services.smsman_service import SMSManService
from workers.rental_monitor import monitor_rental

logger = logging.getLogger(__name__)

router = Router()


# ====================== ORDERS MENU ======================
@router.callback_query(F.data == "orders_menu")
async def orders_menu(callback: CallbackQuery, db_user):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order)
            .where(Order.user_id == db_user.id)
            .order_by(Order.created_at.desc())
            .limit(10)
        )
        orders = result.scalars().all()

    if not orders:
        await callback.message.edit_text(
            "<b>📋 My Orders</b>\n\nNo orders yet.",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    text = "<b>📋 My Orders</b>\n\n"

    for order in orders:
        status_emoji = {
            "PENDING": "⏳",
            "RECEIVED": "✅",
            "CANCELLED": "❌",
            "EXPIRED": "⏰",
            "COMPLETED": "✅"
        }.get(order.status, "❓")

        text += (
            f"{status_emoji} <b>{order.service_name}</b>\n"
            f"📱 <code>{order.number}</code>\n"
            f"🌍 {order.country_name}\n"
            f"💰 ₦{order.cost}\n"
            f"📅 {order.created_at.strftime('%d %b %Y %H:%M')}\n"
        )

        if order.order_type == "ACTIVATION" and order.otp_code:
            text += f"🔑 OTP: <code>{order.otp_code}</code>\n"

        if order.order_type == "RENTAL" and order.rental_duration:
            text += f"⏱ Duration: {order.rental_duration}\n"

        text += "\n==============\n\n"

    await callback.message.edit_text(
        text,
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== REFRESH OTP ======================
@router.callback_query(OrderCallback.filter(F.action == "refresh"))
async def refresh_otp(
    callback: CallbackQuery,
    callback_data: OrderCallback
):
    order_id = callback_data.order_id

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            await callback.answer("Order not found.", show_alert=True)
            return

        order = await OrderService.update_otp(db, order)

    if order.sms_received:
        sms_text = getattr(order, "sms_text", None) or order.otp_code
        await callback.message.edit_text(
            f"✅ <b>SMS Received</b>\n\n"
            f"📱 Number: <code>{order.number}</code>\n"
            f"📦 Service: {order.service_name}\n\n"
            f"💬 Message:\n<code>{sms_text}</code>",
            parse_mode="HTML"
        )
    else:
        await callback.answer("No SMS yet. Still waiting...", show_alert=False)

    await callback.answer()


# ====================== CANCEL ACTIVATION ======================
@router.callback_query(OrderCallback.filter(F.action == "cancel"))
async def cancel_order(
    callback: CallbackQuery,
    callback_data: OrderCallback
):
    order_id = callback_data.order_id

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            await callback.answer("Order not found.", show_alert=True)
            return

        if order.status != "PENDING":
            await callback.answer("Order cannot be cancelled.", show_alert=True)
            return

        await OrderService.cancel_order(db, order)

    await callback.message.edit_text(
        "❌ <b>Order Cancelled</b>\n\nYour number has been cancelled.",
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== CHECK RENTAL SMS ======================
@router.callback_query(OrderCallback.filter(F.action == "sms"))
async def check_rental_sms(
    callback: CallbackQuery,
    callback_data: OrderCallback
):
    order_id = callback_data.order_id

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            await callback.answer("Order not found.", show_alert=True)
            return

    try:
        response = await SMSManService.get_rental_sms(order.request_id)
        sms_list = response.get("sms", [])

        if isinstance(sms_list, dict):
            sms_list = [sms_list]

        if not sms_list:
            await callback.answer("No SMS received yet.", show_alert=False)
            return

        sms_text = "\n==============\n".join(
            f"📩 {sms['message']}\n🕐 {sms.get('time', '')}"
            for sms in sms_list
            if sms.get("message")
        )

        await callback.message.edit_text(
            f"<b>♻️ Rental Number</b>\n\n"
            f"📱 Number:\n<code>{order.number}</code>\n\n"
            f"🌍 Country: {order.country_name}\n"
            f"⏱ Duration: {order.rental_duration}\n\n"
            f"<b>📨 Messages:</b>\n\n"
            f"{sms_text}",
            reply_markup=rental_order_keyboard(order.id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"check_rental_sms failed: {e}")
        await callback.answer("Failed to fetch SMS.", show_alert=True)

    await callback.answer()


# ====================== CLOSE RENTAL ======================
@router.callback_query(OrderCallback.filter(F.action == "close"))
async def close_rental(
    callback: CallbackQuery,
    callback_data: OrderCallback
):
    order_id = callback_data.order_id

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            await callback.answer("Order not found.", show_alert=True)
            return

        await OrderService.cancel_order(db, order)

    await callback.message.edit_text(
        "✅ <b>Rental Closed</b>\n\nYour rental number has been closed.",
        parse_mode="HTML"
    )
    await callback.answer()
