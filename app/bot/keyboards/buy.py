from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def countries_kb(countries: list):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=c)] for c in countries],
        resize_keyboard=True
    )


def services_kb(services: list):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s)] for s in services],
        resize_keyboard=True
    )