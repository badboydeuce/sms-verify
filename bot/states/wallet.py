# bot/states/wallet.py

from aiogram.fsm.state import State, StatesGroup


class WalletStates(StatesGroup):
    enter_amount = State()
    crypto_amount = State()       # ✅ added
    crypto_tx_hash = State()      # ✅ added
