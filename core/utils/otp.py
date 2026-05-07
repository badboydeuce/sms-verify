import re


def extract_otp(message: str):

    patterns = [
        r"\b\d{4,8}\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message
        )

        if match:
            return match.group()

    return None