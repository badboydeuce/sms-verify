# bot/states/buy.py

from aiogram.fsm.state import State, StatesGroup


class BuyStates(StatesGroup):
    search_country = State()
    search_service = State()
