from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "wallet_menu")
async def wallet_menu(callback: CallbackQuery):

    text = """
<b>💰 Wallet</b>

Balance: ₦0.00
"""

    await callback.message.edit_text(
        text,
    )

    await callback.answer()