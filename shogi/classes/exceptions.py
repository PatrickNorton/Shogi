__all__ = [
    "PromotionError",
    "NotPromotableException",
    "PromotedException",
    "DemotedException",
    "IllegalMove",
    "PlayerExit",
    "OtherMove",
    "OtherInput"
]


class PromotionError(Exception):
    """Error in promotion"""


class NotPromotableException(PromotionError):
    """Piece is not promotable."""


class PromotedException(PromotionError):
    """Piece is already promoted."""


class DemotedException(PromotionError):
    """Piece is already demoted."""


class IllegalMove(Exception):
    """The move cannot be made."""
    def __init__(self, errornum):
        from .information import info
        super().__init__(errornum)
        self.int = errornum
        self.message = info.ERRORS[errornum]

    def __str__(self): return self.message

    def __int__(self): return self.int


class PlayerExit(Exception):
    """The player wishes to exit."""


class OtherMove(Exception):
    """An other move was made."""


class OtherInput(Exception):
    """A non-location input was entered."""


class NullCoordError(Exception):
    """A null coordinate was referenced."""