# app/routes/numbers.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from app.bot.keyboards import countries, services, main_menu

from app.services.smsman_api import (
    get_countries,
    get_services,
    buy_number,
    get_sms,
    cancel_number
)

from app.services.wallet_service import WalletService

wallet = WalletService()

# =========================
# 🧠 TEMP STORAGE (replace with DB later)
# =========================
user_sessions = {}
orders = {}

# Example pricing (move to DB later)
PRICES = {
    "whatsapp": 50,
    "telegram": 40,
    "facebook": 30
}

# =========================
# 🌍 BUY NUMBER (STEP 1)
# =========================
async def handle_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text("⏳ Fetching countries...")

    data = get_countries()

    await query.message.edit_text(
        "🌍 Select a country:",
        reply_markup=countries(data)
    )


# =========================
# 🌍 SELECT COUNTRY
# =========================
async def handle_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    country_id = query.data.split("_")[1]

    user_sessions[query.from_user.id] = {
        "country_id": country_id
    }

    await query.message.edit_text("⏳ Fetching services...")

    data = get_services(country_id)

    await query.message.edit_text(
        "📱 Select a service:",
        reply_markup=services(data)
    )


# =========================
# 📱 SELECT SERVICE + BUY
# =========================
async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service_id = query.data.split("_")[1]
    user_id = str(query.from_user.id)

    session = user_sessions.get(query.from_user.id)

    if not session:
        await query.message.edit_text(
            "❌ Session expired.",
            reply_markup=main_menu()
        )
        return

    country_id = session["country_id"]

    price = PRICES.get(service_id, 50)

    # =========================
    # 💰 WALLET CHECK
    # =========================
    balance = wallet.get_balance(user_id)

    if balance < price:
        await query.message.edit_text(
            f"❌ Insufficient balance\n\n"
            f"Balance: ₦{balance}\n"
            f"Required: ₦{price}"
        )
        return

    await query.message.edit_text("⏳ Buying number...")

    # =========================
    # ➖ DEDUCT WALLET
    # =========================
    success = wallet.deduct_balance(
        user_id=user_id,
        amount=price,
        reference=f"SMS-{service_id}"
    )

    if not success:
        await query.message.edit_text("❌ Wallet error.")
        return

    # =========================
    # 📞 BUY NUMBER
    # =========================
    result = buy_number(country_id, service_id)

    if not result or "number" not in result:
        wallet.add_balance(user_id, price)

        await query.message.edit_text(
            "❌ Failed to buy number. Refunded.",
            reply_markup=main_menu()
        )
        return

    number = result["number"]
    order_id = result.get("order_id") or result.get("id")

    # Save order
    orders[user_id] = {
        "order_id": order_id,
        "number": number
    }

    await query.message.edit_text(
        f"📞 Number: `{number}`\n\n"
        "⏳ Waiting for SMS...",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Check SMS", callback_data="check_sms"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")
            ]
        ])
    )


# =========================
# 📩 CHECK SMS
# =========================
async def handle_check_sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    order = orders.get(user_id)

    if not order:
        await query.message.edit_text("❌ No active order.")
        return

    sms_code = get_sms(order["order_id"])

    if not sms_code:
        await query.answer("⏳ No SMS yet", show_alert=True)
        return

    await query.message.edit_text(
        f"✅ OTP:\n\n`{sms_code}`",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


# =========================
# ❌ CANCEL ORDER
# =========================
async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    order = orders.get(user_id)

    if order:
        cancel_number(order["order_id"])

        # NOTE: refund logic can be added here if needed

    orders.pop(user_id, None)

    await query.message.edit_text(
        "❌ Cancelled.",
        reply_markup=main_menu()
    )


# =========================
# 🔗 REGISTER
# =========================
def register_handlers(application):
    application.add_handler(CallbackQueryHandler(handle_buy, pattern="^buy$"))
    application.add_handler(CallbackQueryHandler(handle_country, pattern="^c_"))
    application.add_handler(CallbackQueryHandler(handle_service, pattern="^s_"))
    application.add_handler(CallbackQueryHandler(handle_check_sms, pattern="^check_sms$"))
    application.add_handler(CallbackQueryHandler(handle_cancel, pattern="^cancel_order$"))