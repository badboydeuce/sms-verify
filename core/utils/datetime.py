from datetime import datetime, timedelta


def utc_now():

    return datetime.utcnow()


def activation_expiry():

    return utc_now() + timedelta(
        minutes=20
    )


def remaining_seconds(expires_at):

    seconds = int(
        (expires_at - utc_now()).total_seconds()
    )

    return max(seconds, 0)