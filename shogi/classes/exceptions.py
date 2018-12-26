__all__ = [
    "NotPromotableException",
    "PromotedException",
    "DemotedException",
    "IllegalMove",
    "PlayerExit",
    "OtherMove",
    "OtherInput"
]

class NotPromotableException(Exception):
    pass


class PromotedException(Exception):
    pass


class DemotedException(Exception):
    pass


class IllegalMove(Exception):
    pass


class PlayerExit(Exception):
    pass


class OtherMove(Exception):
    pass


class OtherInput(Exception):
    pass