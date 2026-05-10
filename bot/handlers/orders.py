# bot/handlers/orders.py

import asyncio
import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from bot.callback_factories.orders import OrderCallback
from bot.keyboards.orders import activation_order_keyboard, rental_order_keyboard
from core.database.session import AsyncSessionLocal
from core.models.order import Order
from core.models.rental_sms import RentalSMS
from core.services.order_service import OrderService
from core.services.smsman_service import SMSManService

logger = logging.getLogger(__name__)

router = Router()


def _format_single_order(order, sms_list=None):
    status_emoji = {
        "PENDING": "⏳",
        "RECEIVED": "✅",
        "CANCELLED": "❌",
        "EXPIRED": "⏰",
        "COMPLETED": "✅",
        "ACTIVE": "🟢"
    }.get(order.status, "❓")

    text = (
        f"{status_emoji} <b>{order.service_name}</b>\n"
        f"📱 <code>{order.number}</code>\n"
        f"🌍 {order.country_name}\n"
        f"💰 ₦{order.cost}\n"
        f"📅 {order.created_at.strftime('%d %b %Y %H:%M')}\n"
    )

    if order.order_type == "ACTIVATION":
        if order.otp_code:
            text += f"🔑 OTP: <code>{order.otp_code}</code>\n"

    if order.order_type == "RENTAL":
        text += f"⏱ {order.rental_duration}\n"
        if sms_list:
            text += "\n" + "\n——————\n".join(
                f"💬 Message: {sms.message}\n🕐 Timestamp: {sms.received_at}"
                for sms in sms_list
            )
        else:
            text += "\n⏳ No SMS yet."

    return text


# ====================== ORDERS MENU ======================
@router.callback_query(F.data == "orders_menu")
async def orders_menu(callback: CallbackQuery, db_user):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order)
            .where(Order.user_id == db_user.id)
            .order_by(Order.created_at.desc())
            .limit(5)  # ✅ last 5 orders
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

    async with AsyncSessionLocal() as db:
        for order in orders:
            sms_list = None

            if order.order_type == "RENTAL":
                sms_result = await db.execute(
                    select(RentalSMS)
                    .where(RentalSMS.order_id == order.id)
                    .order_by(RentalSMS.created_at.asc())
                )
                sms_list = sms_result.scalars().all()

            text += _format_single_order(order, sms_list)
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

        sms_result = await db.execute(
            select(RentalSMS)
            .where(RentalSMS.order_id == order_id)
            .order_by(RentalSMS.created_at.asc())
        )
        sms_list = sms_result.scalars().all()

    if not sms_list:
        await callback.answer("No SMS received yet.", show_alert=False)
        await callback.answer()
        return

    sms_text = "\n——————\n".join(
        f"💬 Message: {sms.message}\n🕐 Timestamp: {sms.received_at}"
        for sms in sms_list
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
