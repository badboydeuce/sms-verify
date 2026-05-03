# app/bot/handlers.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from app.bot.keyboards import (
    main_menu,
    countries,
    services,
    payment_menu,
    crypto_menu,
    paystack_amount_menu
)

from app.services.sms_service import SMSService
from app.services.paystack_service import PaystackService
from app.services.wallet_service import WalletService

sms = SMSService()
paystack = PaystackService()
wallet = WalletService()

# 💰 Pricing (you can later move to DB)
PRICES = {
    "whatsapp": 50,
    "telegram": 40,
    "facebook": 30
}


# =========================
# 🚀 START
# =========================
def start(update: Update, context: CallbackContext):
    context.user_data.clear()

    update.message.reply_text(
        "👋 Welcome to DeuceVerify\n\n"
        "🚀 Instant SMS verification gateway\n"
        "🌍 Buy virtual numbers in seconds\n"
        "📩 Receive OTP automatically\n"
        "💰 Pay only for what you use\n\n"
        "Choose an option below 👇",
        reply_markup=main_menu()
    )


# =========================
# 🔘 BUTTON HANDLER
# =========================
def buttons(update: Update, context: CallbackContext):
    q = update.callback_query
    q.answer()

    data = q.data
    user_id = str(q.from_user.id)

    print(f"🔥 CLICKED: {data}")


    # ========================
    # 💰 ADD BALANCE
    # ========================
    if data == "add_balance":
        q.edit_message_text(
            "💰 Add Balance\nChoose payment method:",
            reply_markup=payment_menu()
        )


    # ========================
    # 🇳🇬 PAYSTACK FLOW
    # ========================
    elif data.startswith("paystack_"):
        try:
            amount_naira = int(data.split("_")[1])
            amount_kobo = amount_naira * 100

            email = f"user_{user_id}@deuceverify.com"

            result = paystack.initialize_transaction(
                email=email,
                amount=amount_naira,
                telegram_id=user_id
            )

            if result.get("success"):
                keyboard = [[
                    InlineKeyboardButton(
                        "💳 Pay Now",
                        url=result["authorization_url"]
                    )
                ]]

                q.edit_message_text(
                    f"💳 Pay ₦{amount_naira}\n\nReference: `{result['reference']}`",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            else:
                q.edit_message_text("❌ Payment failed.")

        except Exception as e:
            print(e)
            q.edit_message_text("❌ Error generating payment.")


    # ========================
    # 🌍 BUY FLOW
    # ========================
    elif data == "buy":
        q.edit_message_text("⏳ Loading countries...")

        try:
            data = sms.get_countries()
            q.edit_message_text(
                "🌍 Select country:",
                reply_markup=countries(data)
            )
        except Exception as e:
            print(e)
            q.edit_message_text("❌ Failed to load countries.")


    # ========================
    # 🌍 COUNTRY SELECT
    # ========================
    elif data.startswith("c_"):
        country_id = data.split("_")[1]
        context.user_data["country"] = country_id

        q.edit_message_text("⏳ Loading services...")

        try:
            data = sms.get_services(country_id)
            q.edit_message_text(
                "📱 Select service:",
                reply_markup=services(data)
            )
        except Exception as e:
            print(e)
            q.edit_message_text("❌ Failed to load services.")


    # ========================
    # 📱 SERVICE SELECT + BUY
    # ========================
    elif data.startswith("s_"):
        if "country" not in context.user_data:
            q.edit_message_text("⚠️ Select country first.")
            return

        service_id = data.split("_")[1]
        country_id = context.user_data["country"]

        price = PRICES.get(service_id, 50)

        # 💰 WALLET CHECK
        balance = wallet.get_balance(user_id)

        if balance < price:
            q.edit_message_text(
                f"❌ Insufficient balance\n\n"
                f"Balance: ₦{balance}\n"
                f"Required: ₦{price}"
            )
            return

        q.edit_message_text("⏳ Buying number...")

        # ➖ DEDUCT WALLET
        success = wallet.deduct_balance(
            user_id=user_id,
            amount=price,
            reference=f"SMS-{service_id}"
        )

        if not success:
            q.edit_message_text("❌ Wallet deduction failed.")
            return

        # 📞 BUY NUMBER
        try:
            res = sms.buy_number(country_id, service_id)

            if not res or not res.get("success"):
                wallet.add_balance(user_id, price)
                q.edit_message_text("❌ Failed. Refunded.")
                return

        except Exception as e:
            print(e)
            wallet.add_balance(user_id, price)
            q.edit_message_text("❌ Error. Refunded.")
            return

        # SAVE ORDER
        context.user_data["request_id"] = res["order_id"]
        context.user_data["number"] = res["number"]

        q.edit_message_text(
            f"📱 Number: `{res['number']}`\n"
            f"🆔 ID: `{res['order_id']}`\n\n"
            "⏳ Waiting for OTP...",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Check SMS", callback_data="check_sms"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")
                ]
            ])
        )


    # ========================
    # 📩 CHECK SMS
    # ========================
    elif data == "check_sms":
        request_id = context.user_data.get("request_id")

        if not request_id:
            q.edit_message_text("❌ No active order.")
            return

        try:
            sms_code = sms.get_sms(request_id)
        except Exception as e:
            print(e)
            q.answer("Error checking SMS", show_alert=True)
            return

        if not sms_code:
            q.answer("⏳ No SMS yet", show_alert=True)
            return

        q.edit_message_text(
            f"✅ OTP Received:\n\n`{sms_code}`",
            parse_mode="Markdown",
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
                print(e)

        context.user_data.clear()

        q.edit_message_text("❌ Cancelled.", reply_markup=main_menu())


    # ========================
    # 🏠 HOME
    # ========================
    elif data == "home":
        context.user_data.clear()
        q.edit_message_text("🏠 Main Menu", reply_markup=main_menu())