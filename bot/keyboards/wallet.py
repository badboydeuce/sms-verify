# bot/keyboards/wallet.py

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback_factories.wallet import WalletCallback


def wallet_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="💳 Fund Wallet",
        callback_data=WalletCallback(action="fund").pack()
    )

    kb.button(
        text="📜 Transactions",
        callback_data=WalletCallback(action="history").pack()
    )

    kb.button(
        text="🔙 Back",
        callback_data="main_menu"
    )

    kb.adjust(1)
    return kb.as_markup()


def fund_method_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="🏦 Paystack (Card/Bank)",
        callback_data=WalletCallback(action="paystack").pack()
    )

    kb.button(
        text="₿ Crypto",
        callback_data=WalletCallback(action="crypto").pack()
    )

    kb.button(
        text="🔙 Back",
        callback_data=WalletCallback(action="back_wallet").pack()
    )

    kb.adjust(1)
    return kb.as_markup()


def crypto_coin_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="💎 USDT (TRC20)",
        callback_data=WalletCallback(action="coin_usdt").pack()
    )

    kb.button(
        text="₿ Bitcoin (BTC)",
        callback_data=WalletCallback(action="coin_btc").pack()
    )

    kb.button(
        text="🔷 Ethereum (ETH)",
        callback_data=WalletCallback(action="coin_eth").pack()
    )

    kb.button(
        text="🌕 Litecoin (LTC)",
        callback_data=WalletCallback(action="coin_ltc").pack()
    )

    kb.button(
        text="🔙 Back",
        callback_data=WalletCallback(action="fund").pack()
    )

    kb.adjust(1)
    return kb.as_markup()


def crypto_confirm_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="✅ I've Sent Payment",
        callback_data=WalletCallback(action="crypto_sent").pack()
    )

    kb.button(
        text="❌ Cancel",
        callback_data=WalletCallback(action="back_wallet").pack()
    )

    kb.adjust(1)
    return kb.as_markup()
