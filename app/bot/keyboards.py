from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os

SMS_API_KEY = os.getenv("SMS_API_KEY")


FEATURED_COUNTRIES = [
    ("🇺🇸 USA", "1"),
    ("🇬🇧 UK", "2"),
    ("🇨🇦 Canada", "3"),
    ("🇩🇪 Germany", "4"),
    ("🇫🇷 France", "5"),
    ("🇮🇳 India", "6"),
    ("🇮🇩 Indonesia", "7"),
    ("🇳🇬 Nigeria", "8"),
    ("🇧🇷 Brazil", "9"),
    ("🇿🇦 South Africa", "10"),
]


def fetch_countries():
    url = f"https://api.sms-man.com/stubs/handler_api.php"
    params = {
        "api_key": SMS_API_KEY,
        "action": "getCountries"
    }
    res = requests.get(url, params=params)
    return res.json()


def countries():
    data = fetch_countries()

    keyboard = []

    # ⭐ Featured first
    for name, cid in FEATURED_COUNTRIES:
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"c_{cid}")
        ])

    keyboard.append([InlineKeyboardButton("────────────", callback_data="ignore")])

    # 🌍 Dynamic list (optional section)
    for cid, name in list(data.items())[:20]:
        keyboard.append([
            InlineKeyboardButton(f"🌍 {name}", callback_data=f"c_{cid}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back", callback_data="home")
    ])

    return InlineKeyboardMarkup(keyboard)