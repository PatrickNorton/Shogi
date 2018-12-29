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


class PromotedException(Exception):
    """Piece is already promoted."""


class DemotedException(Exception):
    """Piece is already demoted."""


class IllegalMove(Exception):
    """The move cannot be made."""


class PlayerExit(Exception):
    """The player wishes to exit."""


class OtherMove(Exception):
    """An other move was made."""


class OtherInput(Exception):
    """A non-location input was entered."""

class NullCoordError(Exception):
    """A null coordinate was referenced."""