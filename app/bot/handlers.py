
from telegram import Update
from telegram.ext import CallbackContext
from app.bot.keyboards import main_menu, countries, services
from app.services.sms_service import SMSService

sms = SMSService()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome", reply_markup=main_menu())

def buttons(update: Update, context: CallbackContext):
    q = update.callback_query
    q.answer()
    data = q.data

    if data == "buy":
        q.edit_message_text("Select country", reply_markup=countries())

    elif data.startswith("c_"):
        context.user_data["country"] = int(data.split("_")[1])
        q.edit_message_text("Select service", reply_markup=services())

    elif data.startswith("s_"):
        app_id = int(data.split("_")[1])
        country = context.user_data["country"]

        res = sms.buy_number(country, app_id)
        if "error" in res:
            q.edit_message_text("Error")
            return

        q.edit_message_text(f"Number: {res['number']}\nID: {res['request_id']}")
