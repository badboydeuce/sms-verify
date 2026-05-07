from uuid import uuid4


def generate_reference(
    prefix: str = "DV"
):

    return f"{prefix}-{uuid4().hex[:12].upper()}"