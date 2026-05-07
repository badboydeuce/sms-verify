from aiogram.fsm.state import (
    StatesGroup,
    State
)


class WalletStates(StatesGroup):

    waiting_for_amount = State()
