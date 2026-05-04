from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buy Number")],
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="➕ Fund Wallet")]
        ],
        resize_keyboard=True
    )
