
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from app.bot.handlers import start, buttons
from app.config import settings

def run_bot():
    updater = Updater(settings.BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(buttons))

    updater.start_polling()
    updater.idle()
