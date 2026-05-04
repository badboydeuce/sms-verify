from aiogram import Router, types, F

router = Router()


@router.message(F.text == "📞 Contact Support")
async def contact_support(message: types.Message):

    await message.answer(
        "📞 *Support*\n\n"
        "Need help?\n"
        "Contact us here:\n\n"
        "👉 https://t.me/your_support_username",
        parse_mode="Markdown"
    )
