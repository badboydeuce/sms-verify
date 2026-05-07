def validate_telegram_id(
    telegram_id: int
):

    if not isinstance(
        telegram_id,
        int
    ):

        raise ValueError(
            "Invalid telegram ID"
        )

    return telegram_id