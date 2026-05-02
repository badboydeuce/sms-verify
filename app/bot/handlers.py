from telegram import Update
from telegram.ext import CallbackContext

from app.bot.keyboards import main_menu, countries, services
from app.services.sms_service import SMSService

sms = SMSService()


# =========================
# 🚀 START COMMAND
# =========================
def start(update: Update, context: CallbackContext):
    context.user_data.clear()

    update.message.reply_text(
        "👋 Welcome to DeuceVerify\n\n"
        "🚀 Instant SMS verification gateway\n"
        "🌍 Buy virtual numbers in seconds\n"
        "📩 Receive OTP automatically\n"
        "💰 Pay only for what you use\n\n"
        "Choose an option below to continue 👇",
        reply_markup=main_menu()
    )


# =========================
# 🔘 BUTTON HANDLER
# =========================
def buttons(update: Update, context: CallbackContext):
    q = update.callback_query
    q.answer()

    data = q.data
    print(f"🔥 CLICKED: {data}")  # DEBUG LOG

    # =========================
    # 🌍 BUY FLOW START
    # =========================
    if data == "buy":
        q.edit_message_text(
            "🌍 Select your country",
            reply_markup=countries()
        )

    # =========================
    # 🌍 COUNTRY SELECTED
    # =========================
    elif data.startswith("c_"):
        country_id = int(data.split("_")[1])
        context.user_data["country"] = country_id

        q.edit_message_text(
            "📱 Select service",
            reply_markup=services(country_id)
        )

    # =========================
    # 📱 SERVICE SELECTED
    # =========================
    elif data.startswith("s_"):
        if "country" not in context.user_data:
            q.edit_message_text(
                "⚠️ Please select a country first.",
                reply_markup=main_menu()
            )
            return

        service_id = data.split("_")[1]
        country_id = context.user_data["country"]

        q.edit_message_text("⏳ Purchasing number...")

        try:
            res = sms.buy_number(country_id, service_id)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            q.edit_message_text("❌ System error. Try again later.")
            return

        if not res or "error" in res:
            q.edit_message_text("❌ Failed to buy number. Try again.")
            return

        context.user_data["request_id"] = res.get("request_id")
        context.user_data["number"] = res.get("number")

        q.edit_message_text(
            f"📱 Number: {res['number']}\n"
            f"🆔 ID: {res['request_id']}\n\n"
            "⏳ Waiting for OTP..."
        )

    # =========================
    # 🏠 HOME BUTTON
    # =========================
    elif data == "home":
        q.edit_message_text(
            "🏠 Main Menu",
            reply_markup=main_menu()
        )

    # =========================
    # ⚠️ UNKNOWN ACTION
    # =========================
    else:
        print(f"⚠️ UNKNOWN CALLBACK: {data}")
        q.edit_message_text(
            "⚠️ Unknown action. Returning to menu.",
            reply_markup=main_menu()
        )
