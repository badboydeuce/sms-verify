from aiogram.utils.keyboard import (
    InlineKeyboardBuilder
)

from bot.callback_factories.wallet import (
    WalletCallback
)


def wallet_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="💳 Fund Wallet",
        callback_data=WalletCallback(
            action="fund"
        ).pack()
    )

    kb.button(
        text="📜 Transactions",
        callback_data=WalletCallback(
            action="history"
        ).pack()
    )

    kb.button(
        text="🔙 Back",
        callback_data="main_menu"
    )

    kb.adjust(1)

    return kb.as_markup()
