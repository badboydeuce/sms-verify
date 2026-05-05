from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# =========================
# 🌍 COUNTRIES KEYBOARD
# =========================
def countries_kb(countries: list):

    keyboard = []

    for c in countries:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🌍 {c['title']}",
                callback_data=f"country:{c['id']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# =========================
# 📱 SERVICES KEYBOARD
# =========================
def services_kb(services: list):

    keyboard = []

    for s in services:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📱 {s['name']}",
                callback_data=f"service:{s['id']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# =========================
# 🛒 CONFIRM PURCHASE
# =========================
def confirm_kb():

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Buy Number", callback_data="buy:confirm")
        ],
        [
            InlineKeyboardButton(text="❌ Cancel", callback_data="buy:cancel")
        ]
    ])
