from app.database import init_db
from app.bot.bot import run_bot

if __name__ == "__main__":
    init_db()
    run_bot()
