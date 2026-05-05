from aiogram.fsm.state import State, StatesGroup


class BuyFlow(StatesGroup):
    country = State()
    service = State()
