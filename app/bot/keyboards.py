from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.services.smsman_api import get_countries, get_services
from telegram import ReplyKeyboardMarkup

# =========================
# 🏠 MAIN MENU
# =========================
def main_menu():
    keyboard = [
        ["📲 Buy Number", "📥 Get SMS"],
        ["💰 Wallet", "ℹ️ Help"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ⭐ Featured countries
FEATURED = {
    "1": "🇺🇸 USA",
    "2": "🇬🇧 UK",
    "3": "🇨🇦 Canada",
    "4": "🇩🇪 Germany",
    "5": "🇫🇷 France",
    "6": "🇮🇳 India",
    "7": "🇮🇩 Indonesia",
    "8": "🇳🇬 Nigeria",
}


# =========================
# 🌍 COUNTRIES MENU
# =========================
def countries():
    data = get_countries()

    keyboard = []

    # ⭐ Featured first
    for cid, name in FEATURED.items():
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"c_{cid}")
        ])

    keyboard.append([
        InlineKeyboardButton("────────────", callback_data="ignore")
    ])

    # 🌍 API countries
    for cid, name in list(data.items())[:30]:
        keyboard.append([
            InlineKeyboardButton(f"🌍 {name}", callback_data=f"c_{cid}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back to Menu", callback_data="home")
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================
# 📱 SERVICES MENU
# =========================
def services(country_id: int):
    data = get_services(country_id)

    keyboard = []

    for sid, name in data.items():
        keyboard.append([
            InlineKeyboardButton(f"📱 {name}", callback_data=f"s_{sid}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back to Countries", callback_data="buy")
    ])

    return InlineKeyboardMarkup(keyboard)
