# bot/keyboards/buy.py

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback_factories.buy import BuyCallback


def buy_menu_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="📩 One-Time SMS",
        callback_data=BuyCallback(action="type", value="activation").pack()
    )
    kb.button(
        text="♻️ Rent Number",
        callback_data=BuyCallback(action="type", value="rental").pack()
    )
    kb.button(
        text="🔗 Compatible API",
        callback_data=BuyCallback(action="type", value="compatible").pack()
    )
    kb.button(text="🔙 Back", callback_data="main_menu")
    kb.adjust(1)

    return kb.as_markup()


def rental_duration_keyboard():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="⏱ 1 Hour",
        callback_data=BuyCallback(action="rental_duration", value="hour_1").pack()
    )
    kb.button(
        text="📅 1 Day",
        callback_data=BuyCallback(action="rental_duration", value="day_1").pack()
    )
    kb.button(
        text="📆 1 Week",
        callback_data=BuyCallback(action="rental_duration", value="week_1").pack()
    )
    kb.button(
        text="🗓 1 Month",
        callback_data=BuyCallback(action="rental_duration", value="month_1").pack()
    )
    kb.button(text="🔙 Back", callback_data="buy_menu")
    kb.adjust(2)

    return kb.as_markup()
