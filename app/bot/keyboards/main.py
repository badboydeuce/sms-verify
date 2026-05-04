from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buy Number")],
            [KeyboardButton(text="👤 My Profile"), KeyboardButton(text="➕ Fund Wallet")],
            [KeyboardButton(text="📞 Contact Support")]
        ],
        resize_keyboard=True
    )
