from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from app.bot.keyboards import countries, services, main_menu
from app.services.smsman_api import (
    get_countries,
    get_services,
    buy_number,
    get_sms,
    cancel_number
)

# =========================
# 🧠 TEMP STORAGE (replace with DB later)
# =========================
user_sessions = {}   # user_id -> {country_id, service_id}
orders = {}          # user_id -> {order_id, number}


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
# 🌍 SELECT COUNTRY (STEP 2)
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
# 📱 SELECT SERVICE (STEP 3)
# =========================
async def handle_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service_id = query.data.split("_")[1]
    user_id = query.from_user.id

    session = user_sessions.get(user_id)

    if not session:
        await query.message.edit_text(
            "❌ Session expired. Please start again.",
            reply_markup=main_menu()
        )
        return

    country_id = session["country_id"]

    await query.message.edit_text("⏳ Buying number...")

    result = buy_number(country_id, service_id)

    if not result or "number" not in result:
        await query.message.edit_text(
            "❌ Failed to buy number. Try again later.",
            reply_markup=main_menu()
        )
        return

    number = result["number"]
    order_id = result["id"]

    # Save order
    orders[user_id] = {
        "order_id": order_id,
        "number": number
    }

    await query.message.edit_text(
        f"📞 Number: `{number}`\n\n"
        f"⏳ Waiting for SMS...\n\n"
        f"Click below to check OTP",
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
        await query.message.edit_text(
            "❌ No active order.",
            reply_markup=main_menu()
        )
        return

    order_id = order["order_id"]

    sms = get_sms(order_id)

    if not sms:
        await query.answer("⏳ No SMS yet...", show_alert=True)
        return

    await query.message.edit_text(
        f"✅ OTP Received:\n\n`{sms}`",
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

    if not order:
        await query.message.edit_text(
            "❌ No active order.",
            reply_markup=main_menu()
        )
        return

    order_id = order["order_id"]

    cancel_number(order_id)

    # TODO: refund logic here

    orders.pop(user_id, None)

    await query.message.edit_text(
        "❌ Order cancelled.\n💰 Refund will be processed.",
        reply_markup=main_menu()
    )


# =========================
# 🔗 REGISTER HANDLERS
# =========================
def register_handlers(application):
    application.add_handler(CallbackQueryHandler(handle_buy, pattern="^buy$"))
    application.add_handler(CallbackQueryHandler(handle_country, pattern="^c_"))
    application.add_handler(CallbackQueryHandler(handle_service, pattern="^s_"))
    application.add_handler(CallbackQueryHandler(handle_check_sms, pattern="^check_sms$"))
    application.add_handler(CallbackQueryHandler(handle_cancel, pattern="^cancel_order$"))
