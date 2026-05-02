
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Buy Number", callback_data="buy")]
    ])

def countries():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇸 USA", callback_data="c_1")],
        [InlineKeyboardButton("🇬🇧 UK", callback_data="c_2")]
    ])

def services():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Telegram", callback_data="s_3")]
    ])
