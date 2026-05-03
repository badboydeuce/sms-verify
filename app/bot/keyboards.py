from telegram import InlineKeyboardMarkup, InlineKeyboardButton


# =========================
# 🏠 MAIN MENU
# =========================
def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),
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
# 💰 PAYMENT MENUS
# =========================
def payment_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("₿ Crypto Payment", callback_data="crypto")],
        [InlineKeyboardButton("🇳🇬 Pay with Naira (Paystack)", callback_data="paystack")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="home")]
    ])


def crypto_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("USDT (TRC20)", callback_data="crypto_usdt")],
        [InlineKeyboardButton("BTC (Bitcoin)", callback_data="crypto_btc")],
        [InlineKeyboardButton("🔙 Back", callback_data="add_balance")]
    ])


def paystack_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Generate Payment Link", callback_data="paystack_create")],
        [InlineKeyboardButton("🔙 Back", callback_data="add_balance")]
    ])


def paystack_amount_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("₦1,000", callback_data="paystack_1000")],
        [InlineKeyboardButton("₦2,000", callback_data="paystack_2000")],
        [InlineKeyboardButton("₦5,000", callback_data="paystack_5000")],
        [InlineKeyboardButton("₦10,000", callback_data="paystack_10000")],
        [InlineKeyboardButton("₦20,000", callback_data="paystack_20000")],
        [InlineKeyboardButton("🔙 Back", callback_data="paystack")]
    ])


# =========================
# ⭐ FEATURED COUNTRIES
# =========================
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
def countries(data: dict):
    keyboard = []

    # ⭐ Featured countries
    for cid, name in FEATURED.items():
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"c_{cid}")
        ])

    keyboard.append([
        InlineKeyboardButton("────────────", callback_data="ignore")
    ])

    # 🌍 API countries (limit + avoid duplicates)
    for cid, name in list(data.items())[:30]:
        if cid not in FEATURED:
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
def services(data: dict):
    keyboard = []

    for sid, name in data.items():
        keyboard.append([
            InlineKeyboardButton(f"📱 {name}", callback_data=f"s_{sid}")
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back to Countries", callback_data="buy")
    ])

    return InlineKeyboardMarkup(keyboard)
