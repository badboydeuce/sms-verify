from aiogram import Router, types, F

router = Router()


@router.message(F.text == "📞 Contact Support")
async def contact_support(message: types.Message):

    await message.answer(
        "📞 *Support*\n\n"
        "Need help?\n"
        "Contact us here:\n\n"
        "👉 https://t.me/DEUCE_VERIFY_ADMIN",
        parse_mode="Markdown"
    )
