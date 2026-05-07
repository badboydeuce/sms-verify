from core.exceptions.order import (
    UnauthorizedOrderAccess
)


def validate_order_owner(
    order_user_id: int,
    current_user_id: int
):

    if order_user_id != current_user_id:

        raise UnauthorizedOrderAccess()