from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Wallet Balance", callback_data="wallet"),
            InlineKeyboardButton("🌍 Buy Number", callback_data="buy")
        ],
        [
            InlineKeyboardButton("📊 My Orders", callback_data="orders"),
            InlineKeyboardButton("👤 My Profile", callback_data="profile")
        ],
        [
            InlineKeyboardButton("⚙️ Help / Support", callback_data="help")
        ]
    ])


def countries():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇸 USA", callback_data="c_1"),
            InlineKeyboardButton("🇬🇧 UK", callback_data="c_2")
        ],
        [
            InlineKeyboardButton("🇮🇩 Indonesia", callback_data="c_3"),
            InlineKeyboardButton("🇳🇬 Nigeria", callback_data="c_4")
        ],
        [
            InlineKeyboardButton("🌍 More Countries", callback_data="more_countries")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="home")
        ]
    ])


def services():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 WhatsApp", callback_data="s_1"),
            InlineKeyboardButton("✈️ Telegram", callback_data="s_2")
        ],
        [
            InlineKeyboardButton("📧 Google", callback_data="s_3"),
            InlineKeyboardButton("📘 Facebook", callback_data="s_4")
        ],
        [
            InlineKeyboardButton("🎵 TikTok", callback_data="s_5"),
            InlineKeyboardButton("📱 Other", callback_data="s_99")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="buy")
        ]
    ])