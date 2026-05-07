from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(
    F.data == "orders_menu"
)
async def orders_menu(
    callback: CallbackQuery
):

    await callback.message.edit_text(
        "<b>📋 Active Orders</b>"
    )

    await callback.answer()
