from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# =========================
# 🌍 COUNTRIES KEYBOARD
# =========================
def countries_kb(countries: list):

    buttons = []

    for c in countries:
        buttons.append([
            InlineKeyboardButton(
                text=f"🌍 {c['title']}",
                callback_data=f"country:{c['id']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# 📱 SERVICES KEYBOARD
# =========================
def services_kb(services: list):

    buttons = []

    for s in services:
        buttons.append([
            InlineKeyboardButton(
                text=f"📱 {s['name']}",
                callback_data=f"service:{s['id']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# 🛒 CONFIRM PURCHASE
# =========================
def confirm_buy_kb():

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm Buy", callback_data="buy:confirm")
        ],
        [
            InlineKeyboardButton(text="❌ Cancel", callback_data="buy:cancel")
        ]
    ])
