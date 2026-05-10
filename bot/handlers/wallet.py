# bot/handlers/wallet.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import httpx
import logging

from bot.states.wallet import WalletStates
from bot.keyboards.wallet import (
    wallet_keyboard,
    fund_method_keyboard,
    crypto_coin_keyboard,
    crypto_confirm_keyboard
)
from bot.callback_factories.wallet import WalletCallback
from core.config import API_BASE_URL, ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)

# Wallet addresses
CRYPTO_WALLETS = {
    "usdt": {
        "name": "USDT (TRC20)",
        "address": "THwd3hLHS9zsr8y75Tuytn5LScW5fZ2aSo",
        "network": "Tron (TRC20)",
        "symbol": "USDT",
        "coingecko_id": "tether"
    },
    "btc": {
        "name": "Bitcoin (BTC)",
        "address": "39SE1MXh66E4gtMYD7MutN1vADj6bgiZSR",
        "network": "Bitcoin",
        "symbol": "BTC",
        "coingecko_id": "bitcoin"
    },
    "eth": {
        "name": "Ethereum (ERC20)",
        "address": "0xfdc241a1c517447cdcf30a957f43797bb26adb78",
        "network": "Ethereum (ERC20)",
        "symbol": "ETH",
        "coingecko_id": "ethereum"
    },
    "ltc": {
        "name": "Litecoin (LTC)",
        "address": "LXaA3b1odQrZVfkde1v3mF6NwpyGVXrX5J",
        "network": "Litecoin",
        "symbol": "LTC",
        "coingecko_id": "litecoin"
    }
}


async def get_crypto_rate(coingecko_id: str) -> float:
    """Fetch live NGN rate from CoinGecko."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": coingecko_id,
                    "vs_currencies": "ngn"
                }
            )
            data = response.json()
            return float(data[coingecko_id]["ngn"])
    except Exception as e:
        logger.error(f"Failed to fetch NGN rate: {e}")
        return 0.0


async def get_crypto_rate_usd(coingecko_id: str) -> float:
    """Fetch live USD rate from CoinGecko."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": coingecko_id,
                    "vs_currencies": "usd"
                }
            )
            data = response.json()
            return float(data[coingecko_id]["usd"])
    except Exception as e:
        logger.error(f"Failed to fetch USD rate: {e}")
        return 0.0


# ====================== WALLET MENU ======================
@router.callback_query(F.data == "wallet_menu")
async def wallet_menu(callback: CallbackQuery):
    await callback.answer("💰 Opening Wallet...", show_alert=False)
    try:
        await callback.message.answer(
            "💰 <b>Wallet Menu</b>\n\nChoose an option:",
            reply_markup=wallet_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send wallet menu: {e}")
        await callback.answer("Failed to open menu", show_alert=True)


# ====================== BACK TO WALLET ======================
@router.callback_query(WalletCallback.filter(F.action == "back_wallet"))
async def back_to_wallet(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💰 <b>Wallet Menu</b>\n\nChoose an option:",
        reply_markup=wallet_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== FUND WALLET ======================
@router.callback_query(WalletCallback.filter(F.action == "fund"))
async def fund_wallet_callback(callback: CallbackQuery):
    await callback.message.answer(
        "💳 <b>Fund Your Wallet</b>\n\nChoose payment method:",
        reply_markup=fund_method_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== PAYSTACK ======================
@router.callback_query(WalletCallback.filter(F.action == "paystack"))
async def paystack_fund(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "💳 <b>Fund via Paystack</b>\n\n"
        "Please enter the amount you want to fund:\n"
        "• Minimum: ₦1,500\n\n"
        "Send /cancel at any time to cancel.",
        parse_mode="HTML"
    )
    await state.set_state(WalletStates.enter_amount)
    await callback.answer()


# ====================== PROCESS PAYSTACK AMOUNT ======================
@router.message(WalletStates.enter_amount)
async def process_fund_amount(message: Message, state: FSMContext):
    raw = message.text.strip()

    if raw == "/cancel":
        await state.clear()
        await message.answer("❌ Funding cancelled.")
        return

    try:
        amount = float(raw)
    except ValueError:
        await message.answer(
            "⚠️ Invalid amount. Please enter a number e.g. <b>2000</b>",
            parse_mode="HTML"
        )
        return

    if amount < 1500:
        await message.answer(
            "⚠️ Minimum funding amount is ₦1,500. Please enter a higher amount."
        )
        return

    await state.clear()

    telegram_id = message.from_user.id

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/wallet/fund",
                json={"telegram_id": telegram_id, "amount": amount}
            )
            response.raise_for_status()
            data = response.json()

        await message.answer(
            f"✅ <b>Payment Link Generated</b>\n\n"
            f"Click the link below to complete your payment:\n"
            f"{data['authorization_url']}\n\n"
            f"Reference: <code>{data['reference']}</code>",
            parse_mode="HTML"
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Fund wallet API error: {e}")
        await message.answer("❌ Failed to generate payment link. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error funding wallet: {e}")
        await message.answer("❌ Something went wrong. Please try again later.")


# ====================== CRYPTO SELECTION ======================
@router.callback_query(WalletCallback.filter(F.action == "crypto"))
async def crypto_fund(callback: CallbackQuery):
    await callback.message.answer(
        "₿ <b>Fund via Crypto</b>\n\nSelect your preferred cryptocurrency:",
        reply_markup=crypto_coin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== SHOW CRYPTO ADDRESS ======================
@router.callback_query(WalletCallback.filter(F.action.startswith("coin_")))
async def show_crypto_address(
    callback: CallbackQuery,
    callback_data: WalletCallback,
    state: FSMContext
):
    coin_key = callback_data.action.replace("coin_", "")
    coin = CRYPTO_WALLETS.get(coin_key)

    if not coin:
        await callback.answer("Invalid coin selected.", show_alert=True)
        return

    # Fetch live rates
    rate_ngn = await get_crypto_rate(coin["coingecko_id"])
    rate_usd = await get_crypto_rate_usd(coin["coingecko_id"])

    # Calculate $10 minimum in NGN
    usd_to_ngn = rate_ngn / rate_usd if rate_usd else 0
    min_ngn = round(10 * usd_to_ngn, 2)

    rate_text = f"📈 1 {coin['symbol']} = ₦{rate_ngn:,.2f}" if rate_ngn else "📈 Rate unavailable"
    min_text = f"≈ ₦{min_ngn:,.2f}" if min_ngn else ""

    await state.update_data(
        coin_key=coin_key,
        min_ngn=min_ngn
    )
    await state.set_state(WalletStates.crypto_amount)

    await callback.message.answer(
        f"<b>{coin['name']} Payment</b>\n\n"
        f"Send your crypto to the address below:\n\n"
        f"🔗 Network: <b>{coin['network']}</b>\n"
        f"📋 Address:\n<code>{coin['address']}</code>\n\n"
        f"{rate_text}\n"
        f"⚠️ Minimum: <b>$10</b> ({min_text})\n"
        f"⚠️ Network fees paid by you\n\n"
        f"Please enter the <b>NGN amount</b> you want to fund:\n\n"
        f"Send /cancel to cancel.",
        reply_markup=crypto_confirm_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# ====================== PROCESS CRYPTO AMOUNT ======================
@router.message(WalletStates.crypto_amount)
async def process_crypto_amount(message: Message, state: FSMContext):
    raw = message.text.strip()

    if raw == "/cancel":
        await state.clear()
        await message.answer("❌ Cancelled.")
        return

    try:
        amount = float(raw)
    except ValueError:
        await message.answer(
            "⚠️ Invalid amount. Please enter a number e.g. <b>2000</b>",
            parse_mode="HTML"
        )
        return

    data = await state.get_data()
    coin_key = data.get("coin_key")
    min_ngn = data.get("min_ngn", 0)
    coin = CRYPTO_WALLETS.get(coin_key)

    # Validate $10 minimum
    if amount < min_ngn:
        await message.answer(
            f"⚠️ Minimum crypto funding is <b>$10</b> (≈ ₦{min_ngn:,.2f}).\n"
            f"Please enter a higher amount.",
            parse_mode="HTML"
        )
        return

    rate_ngn = await get_crypto_rate(coin["coingecko_id"])
    crypto_amount = amount / rate_ngn if rate_ngn else 0

    await state.update_data(ngn_amount=amount, crypto_amount=crypto_amount)
    await state.set_state(WalletStates.crypto_tx_hash)

    await message.answer(
        f"💱 <b>Payment Summary</b>\n\n"
        f"NGN Amount: ₦{amount:,.2f}\n"
        f"Crypto Amount: <b>{crypto_amount:.8f} {coin['symbol']}</b>\n"
        f"Network: {coin['network']}\n\n"
        f"📋 Send exactly to:\n<code>{coin['address']}</code>\n\n"
        f"⚠️ Network fees are paid by you on top of this amount.\n\n"
        f"After sending, please enter your <b>transaction hash/ID</b> below so admin can verify:",
        parse_mode="HTML"
    )


# ====================== PROCESS TX HASH ======================
@router.message(WalletStates.crypto_tx_hash)
async def process_tx_hash(message: Message, state: FSMContext):
    tx_hash = message.text.strip()

    if tx_hash == "/cancel":
        await state.clear()
        await message.answer("❌ Cancelled.")
        return

    data = await state.get_data()
    coin_key = data.get("coin_key")
    ngn_amount = data.get("ngn_amount")
    crypto_amount = data.get("crypto_amount")
    coin = CRYPTO_WALLETS.get(coin_key)

    await state.clear()

    user = message.from_user

    # Notify user
    await message.answer(
        f"✅ <b>Payment Submitted</b>\n\n"
        f"Your payment is being reviewed by admin.\n"
        f"You will be credited once confirmed.\n\n"
        f"💰 Amount: ₦{ngn_amount:,.2f}\n"
        f"🪙 Crypto: {crypto_amount:.8f} {coin['symbol']}\n"
        f"🔗 TX Hash: <code>{tx_hash}</code>",
        parse_mode="HTML"
    )

    # Notify admin
    for admin_id in ADMIN_IDS:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{message.bot.token}/sendMessage",
                    json={
                        "chat_id": admin_id,
                        "text": (
                            f"🔔 <b>Crypto Payment Request</b>\n\n"
                            f"👤 User: @{user.username or 'N/A'}\n"
                            f"🆔 ID: <code>{user.id}</code>\n\n"
                            f"💰 NGN Amount: ₦{ngn_amount:,.2f}\n"
                            f"🪙 Crypto: {crypto_amount:.8f} {coin['symbol']}\n"
                            f"🔗 Network: {coin['network']}\n"
                            f"📋 TX Hash: <code>{tx_hash}</code>\n\n"
                            f"Use /credit {user.id} {ngn_amount} to credit this user."
                        ),
                        "parse_mode": "HTML"
                    }
                )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
