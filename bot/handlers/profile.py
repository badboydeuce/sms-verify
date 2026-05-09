# bot/handlers/profile.py

from aiogram import Router, F
from aiogram.types import CallbackQuery

import httpx
import logging

from core.config import API_BASE_URL

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "profile_menu")
async def profile_menu(callback: CallbackQuery):

    user = callback.from_user

    # Fetch wallet balance from API
    balance = "N/A"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL.rstrip('/')}/api/wallet/balance/{user.id}"
            )
            if response.status_code == 200:
                data = response.json()
                balance = f"₦{data['balance']:,.2f}"
    except Exception as e:
        logger.error(f"Failed to fetch balance for {user.id}: {e}")

    text = f"""<b>👤 Profile</b>

ID: <code>{user.id}</code>
Username: @{user.username}
💰 Balance: {balance}"""

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()
