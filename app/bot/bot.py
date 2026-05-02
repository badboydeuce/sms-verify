import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from app.bot.handlers import start, buttons
from app.config import settings


# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================
# BOT START FUNCTION
# =========================
def run_bot():
    try:
        updater = Updater(settings.BOT_TOKEN, use_context=True)
        dp = updater.dispatcher

        # =========================
        # HANDLERS
        # =========================
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CallbackQueryHandler(buttons))

        logger.info("🚀 Bot is starting...")

        # =========================
        # START BOT
        # =========================
        updater.start_polling()
        updater.idle()

    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise