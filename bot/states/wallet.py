from aiogram.fsm.state import (
    State,
    StatesGroup
)


class WalletStates(
    StatesGroup
):

    enter_amount = State()