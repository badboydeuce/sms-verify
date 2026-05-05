from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Buy Number")],
        [KeyboardButton(text="👤 My Profile"), KeyboardButton(text="➕ Fund Wallet")],
        [KeyboardButton(text="📞 Contact Support")]
    ],
    resize_keyboard=True
)