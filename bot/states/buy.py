from aiogram.fsm.state import (
    StatesGroup,
    State
)


class BuyStates(StatesGroup):

    choosing_type = State()

    choosing_country = State()

    choosing_service = State()

    confirming_order = State()

    choosing_rental_type = State()

    choosing_rental_duration = State()
