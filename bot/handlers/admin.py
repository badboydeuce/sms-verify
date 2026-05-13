# bot/handlers/admin.py

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import httpx
import logging

from bot.handlers.filters.admin import AdminFilter
from bot.keyboards.admin import admin_keyboard
from bot.callback_factories.admin import AdminCallback
from core.config import API_BASE_URL

router = Router()
logger = logging.getLogger(__name__)


# ====================== ADMIN PANEL ======================
@router.message(Command("admin"), AdminFilter())
async def admin_panel(message: Message):
    await message.answer(
        "<b>🛠 Admin Panel</b>\n\n"
        "Available commands:\n"
        "/credit &lt;telegram_id&gt; &lt;amount&gt;\n"
        "/debit &lt;telegram_id&gt; &lt;amount&gt;\n"
        "/user &lt;telegram_id&gt;\n"
        "/broadcast &lt;message&gt;",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


# ====================== USERS BUTTON ======================
@router.callback_query(AdminCallback.filter(F.action == "users"))
async def admin_users(callback: CallbackQuery):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/admin/stats")
            response.raise_for_status()
            data = response.json()

        await callback.message.answer(
            f"👥 <b>Users</b>\n\n"
            f"Total Registered: <b>{data['total_users']}</b>\n"
            f"Total Wallet Balance: ₦{data['total_wallet_balance']:,.2f}",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"admin_users failed: {e}")
        await callback.answer("❌ Failed to fetch users.", show_alert=True)

    await callback.answer()


# ====================== ORDERS BUTTON ======================
@router.callback_query(AdminCallback.filter(F.action == "orders"))
async def admin_orders(callback: CallbackQuery):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/admin/stats")
            response.raise_for_status()
            data = response.json()

        status_lines = "\n".join(
            f"• {status}: {count}"
            for status, count in data.get("orders_by_status", {}).items()
        )

        await callback.message.answer(
            f"📦 <b>Orders</b>\n\n"
            f"Total Orders: <b>{data['total_orders']}</b>\n\n"
            f"<b>By Status:</b>\n{status_lines or 'No orders yet'}",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"admin_orders failed: {e}")
        await callback.answer("❌ Failed to fetch orders.", show_alert=True)

    await callback.answer()


# ====================== REVENUE BUTTON ======================
@router.callback_query(AdminCallback.filter(F.action == "revenue"))
async def admin_revenue(callback: CallbackQuery):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/admin/stats")
            response.raise_for_status()
            data = response.json()

        await callback.message.answer(
            f"💰 <b>Revenue</b>\n\n"
            f"Total Revenue: ₦{data['total_revenue']:,.2f}\n"
            f"Total Wallet Balance: ₦{data['total_wallet_balance']:,.2f}",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"admin_revenue failed: {e}")
        await callback.answer("❌ Failed to fetch revenue.", show_alert=True)

    await callback.answer()


# ====================== CREDIT USER ======================
@router.message(Command("credit"), AdminFilter())
async def credit_user(message: Message):
    parts = message.text.split()

    if len(parts) != 3:
        await message.answer(
            "Usage: /credit &lt;telegram_id&gt; &lt;amount&gt;\n"
            "Example: /credit 123456789 5000"
        )
        return

    try:
        telegram_id = int(parts[1])
        amount = float(parts[2])
    except ValueError:
        await message.answer("❌ Invalid telegram_id or amount.")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/admin/credit",
                json={"telegram_id": telegram_id, "amount": amount}
            )
            response.raise_for_status()
            data = response.json()

        await message.answer(
            f"✅ <b>User Credited</b>\n\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n"
            f"💰 Amount: ₦{amount:,.2f}\n"
            f"💳 New Balance: ₦{data['new_balance']:,.2f}",
            parse_mode="HTML"
        )

        await message.bot.send_message(
            chat_id=telegram_id,
            text=(
                f"✅ <b>Wallet Credited</b>\n\n"
                f"₦{amount:,.2f} has been added to your wallet.\n"
                f"💳 New Balance: ₦{data['new_balance']:,.2f}"
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Credit user failed: {e}")
        await message.answer("❌ Failed to credit user. Please try again.")


# ====================== DEBIT USER ======================
@router.message(Command("debit"), AdminFilter())
async def debit_user(message: Message):
    parts = message.text.split()

    if len(parts) != 3:
        await message.answer(
            "Usage: /debit &lt;telegram_id&gt; &lt;amount&gt;\n"
            "Example: /debit 123456789 2000"
        )
        return

    try:
        telegram_id = int(parts[1])
        amount = float(parts[2])
    except ValueError:
        await message.answer("❌ Invalid telegram_id or amount.")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/admin/debit",
                json={"telegram_id": telegram_id, "amount": amount}
            )
            response.raise_for_status()
            data = response.json()

        await message.answer(
            f"✅ <b>User Debited</b>\n\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n"
            f"💰 Amount: ₦{amount:,.2f}\n"
            f"💳 New Balance: ₦{data['new_balance']:,.2f}",
            parse_mode="HTML"
        )

        await message.bot.send_message(
            chat_id=telegram_id,
            text=(
                f"⚠️ <b>Wallet Debited</b>\n\n"
                f"₦{amount:,.2f} has been deducted from your wallet.\n"
                f"💳 New Balance: ₦{data['new_balance']:,.2f}\n\n"
                f"If you have questions, please contact support."
            ),
            parse_mode="HTML"
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            await message.answer("❌ Insufficient balance to debit.")
        elif e.response.status_code == 404:
            await message.answer("❌ User not found.")
        else:
            await message.answer("❌ Failed to debit user.")
    except Exception as e:
        logger.error(f"Debit user failed: {e}")
        await message.answer("❌ Failed to debit user. Please try again.")


# ====================== VIEW USER ======================
@router.message(Command("user"), AdminFilter())
async def view_user(message: Message):
    parts = message.text.split()

    if len(parts) != 2:
        await message.answer(
            "Usage: /user &lt;telegram_id&gt;\n"
            "Example: /user 123456789"
        )
        return

    try:
        telegram_id = int(parts[1])
    except ValueError:
        await message.answer("❌ Invalid telegram_id.")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/api/admin/user/{telegram_id}"
            )
            response.raise_for_status()
            data = response.json()

        await message.answer(
            f"👤 <b>User Profile</b>\n\n"
            f"🆔 Telegram ID: <code>{data['telegram_id']}</code>\n"
            f"👤 Username: @{data.get('username') or 'N/A'}\n"
            f"💳 Balance: ₦{data['balance']:,.2f}\n"
            f"📦 Total Orders: {data['total_orders']}\n"
            f"🛡 Admin: {'Yes' if data['is_admin'] else 'No'}\n"
            f"📅 Joined: {data['created_at']}",
            parse_mode="HTML"
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer("❌ User not found.")
        else:
            await message.answer("❌ Failed to fetch user.")
    except Exception as e:
        logger.error(f"View user failed: {e}")
        await message.answer("❌ Failed to fetch user. Please try again.")


# ====================== BROADCAST ======================
@router.message(Command("broadcast"), AdminFilter())
async def broadcast(message: Message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Usage: /broadcast &lt;message&gt;\n"
            "Example: /broadcast We have exciting new features!"
        )
        return

    broadcast_text = parts[1]
    await message.answer("⏳ Sending broadcast...")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/admin/broadcast",
                json={"message": broadcast_text}
            )
            response.raise_for_status()
            data = response.json()

        delivered = 0
        failed = 0

        for telegram_id in data["telegram_ids"]:
            try:
                await message.bot.send_message(
                    chat_id=telegram_id,
                    text=f"📢 <b>Announcement</b>\n\n{broadcast_text}",
                    parse_mode="HTML"
                )
                delivered += 1
            except Exception:
                failed += 1

        await message.answer(
            f"✅ <b>Broadcast Complete</b>\n\n"
            f"👥 Delivered: {delivered}\n"
            f"❌ Failed: {failed}",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Broadcast failed: {e}")
        await message.answer("❌ Broadcast failed. Please try again.")
