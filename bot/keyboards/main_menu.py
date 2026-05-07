from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="📱 Buy Number",
        callback_data="buy_menu"
    )

    kb.button(
        text="💰 Wallet",
        callback_data="wallet_menu"
    )

    kb.button(
        text="📋 My Orders",
        callback_data="orders_menu"
    )

    kb.button(
        text="👤 Profile",
        callback_data="profile_menu"
    )

    kb.button(
        text="❓ Support",
        callback_data="support_menu"
    )

    kb.adjust(2)

    return kb.as_markup()