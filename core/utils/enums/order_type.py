from enum import Enum


class OrderType(str, Enum):

    ACTIVATION = "activation"

    RENTAL = "rental"