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
    """Piece is not promotable."""
    pass


class PromotedException(Exception):
    """Piece is already promoted."""
    pass


class DemotedException(Exception):
    """Piece is already demoted."""
    pass


class IllegalMove(Exception):
    """The move cannot be made."""
    pass


class PlayerExit(Exception):
    """The player wishes to exit."""
    pass


class OtherMove(Exception):
    """An other move was made."""
    pass


class OtherInput(Exception):
    """A non-location input was entered."""
    pass