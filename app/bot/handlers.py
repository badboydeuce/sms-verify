from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from app.bot.keyboards import (
    main_menu,
    countries,
    services,
    payment_menu,
    crypto_menu,
    paystack_menu,
    paystack_amount_menu
)

from app.services.sms_service import SMSService
from app.services.paystack_service import paystack

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
    user_id = q.from_user.id

    print(f"🔥 CLICKED: {data}")


    # ========================
    # 💰 ADD BALANCE FLOW
    # ========================
    if data == "add_balance":
        q.edit_message_text(
            "💰 **Add Balance**\n\nChoose payment method:",
            reply_markup=payment_menu(),
            parse_mode='Markdown'
        )

    elif data == "crypto":
        q.edit_message_text(
            "🔗 **Crypto Payment**\n\nSelect cryptocurrency:",
            reply_markup=crypto_menu(),
            parse_mode='Markdown'
        )

    elif data.startswith("crypto_"):
        coin = data.split("_")[1]
        q.edit_message_text(
            f"🔄 Generating {coin.upper()} deposit address...\n\nPlease wait."
        )

    # ========================
    # 🇳🇬 PAYSTACK FLOW
    # ========================
    elif data == "paystack":
        q.edit_message_text(
            "🇳🇬 **Pay with Naira via Paystack**\n\nChoose amount:",
            reply_markup=paystack_amount_menu(),
            parse_mode='Markdown'
        )

    elif data.startswith("paystack_"):
        try:
            amount_naira = int(data.split("_")[1])
            amount_kobo = amount_naira * 100

            email = f"user_{user_id}@deuceverify.com"

            result = paystack.initialize_transaction(
                email=email,
                amount=amount_kobo,
                user_id=user_id
            )

            if result.get("success"):
                paystack.save_payment_record(result["reference"], user_id)

                keyboard = [[
                    InlineKeyboardButton(
                        "💳 Pay Now",
                        url=result["authorization_url"]
                    )
                ]]

                q.edit_message_text(
                    text=f"✅ **Payment Link Generated**\n\n"
                         f"Amount: **₦{amount_naira:,}**\n"
                         f"Reference: `{result['reference']}`\n\n"
                         f"Click below to complete payment:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            else:
                q.edit_message_text("❌ Failed to generate payment link.")

        except Exception as e:
            print(f"❌ PAYSTACK ERROR: {e}")
            q.edit_message_text("❌ Payment error. Try again.")


    # ========================
    # 🌍 BUY FLOW
    # ========================
    elif data == "buy":
        q.edit_message_text("⏳ Fetching countries...")

        try:
            data = sms.get_countries()
        except Exception as e:
            print(f"❌ ERROR: {e}")
            q.edit_message_text("❌ Failed to load countries.")
            return

        q.edit_message_text(
            "🌍 Select your country:",
            reply_markup=countries(data)
        )


    elif data.startswith("c_"):
        country_id = data.split("_")[1]
        context.user_data["country"] = country_id

        q.edit_message_text("⏳ Fetching services...")

        try:
            data = sms.get_services(country_id)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            q.edit_message_text("❌ Failed to load services.")
            return

        q.edit_message_text(
            "📱 Select service:",
            reply_markup=services(data)
        )


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
            print(f"❌ BUY ERROR: {e}")
            q.edit_message_text("❌ System error. Try again.")
            return

        if not res or "error" in res:
            q.edit_message_text("❌ Failed to buy number.")
            return

        context.user_data["request_id"] = res.get("request_id")
        context.user_data["number"] = res.get("number")

        q.edit_message_text(
            f"📱 Number: `{res['number']}`\n"
            f"🆔 ID: `{res['request_id']}`\n\n"
            "⏳ Waiting for OTP...\n\n"
            "Click below to check SMS",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Check SMS", callback_data="check_sms"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")
                ]
            ])
        )


    # ========================
    # 📩 CHECK OTP
    # ========================
    elif data == "check_sms":
        request_id = context.user_data.get("request_id")

        if not request_id:
            q.edit_message_text("❌ No active request.")
            return

        try:
            sms_code = sms.get_sms(request_id)
        except Exception as e:
            print(f"❌ SMS ERROR: {e}")
            q.answer("Error checking SMS", show_alert=True)
            return

        if not sms_code:
            q.answer("⏳ No SMS yet...", show_alert=True)
            return

        q.edit_message_text(
            f"✅ OTP Received:\n\n`{sms_code}`",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )


    # ========================
    # ❌ CANCEL ORDER
    # ========================
    elif data == "cancel_order":
        request_id = context.user_data.get("request_id")

        if request_id:
            try:
                sms.cancel_number(request_id)
            except Exception as e:
                print(f"❌ CANCEL ERROR: {e}")

        context.user_data.clear()

        q.edit_message_text(
            "❌ Order cancelled.\n💰 Refund processing...",
            reply_markup=main_menu()
        )


    # ========================
    # 🏠 HOME
    # ========================
    elif data == "home":
        context.user_data.clear()

        q.edit_message_text(
            "🏠 Main Menu",
            reply_markup=main_menu()
        )
