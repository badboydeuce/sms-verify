from telegram import InlineKeyboardMarkup, InlineKeyboardButton


# ⭐ FEATURED COUNTRIES (POPULAR FIRST)
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


# 🌍 OPTIONAL: EXTENDED SMS-MAN STYLE COUNTRY LIST
MORE_COUNTRIES = [
    ("🇷🇺 Russia", "11"),
    ("🇺🇦 Ukraine", "12"),
    ("🇰🇿 Kazakhstan", "13"),
    ("🇵🇱 Poland", "14"),
    ("🇮🇹 Italy", "15"),
    ("🇪🇸 Spain", "16"),
    ("🇹🇷 Turkey", "17"),
    ("🇲🇽 Mexico", "18"),
    ("🇦🇷 Argentina", "19"),
    ("🇵🇭 Philippines", "20"),
]


# 📱 SMS-MAN SERVICE MAPPING (IMPORTANT)
SERVICES = [
    ("📱 WhatsApp", "wa"),
    ("✈️ Telegram", "tg"),
    ("📧 Google", "go"),
    ("📘 Facebook", "fb"),
    ("🎵 TikTok", "tt"),
    ("📸 Instagram", "ig"),
]


# =========================
# 🏠 MAIN MENU
# =========================
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


# =========================
# 🌍 COUNTRY MENU
# =========================
def countries():
    keyboard = []

    # ⭐ Featured countries first
    for name, cid in FEATURED_COUNTRIES:
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"c_{cid}")
        ])

    keyboard.append([
        InlineKeyboardButton("────────────", callback_data="ignore")
    ])

    # 🌍 More countries section
    for name, cid in MORE_COUNTRIES:
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"c_{cid}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back to Menu", callback_data="home")
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================
# 📱 SERVICE MENU
# =========================
def services():
    keyboard = []

    # Main services (SMS-Man mapping style)
    for name, sid in SERVICES:
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"s_{sid}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back to Countries", callback_data="buy")
    ])

    return InlineKeyboardMarkup(keyboard)