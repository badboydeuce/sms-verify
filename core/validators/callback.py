def validate_callback_data(
    callback_data: str
):

    if len(callback_data) > 64:

        raise ValueError(
            "Callback data too long"
        )

    return callback_data