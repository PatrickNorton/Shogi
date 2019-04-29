__all__ = [
    "PromotionError",
    "NotPromotableException",
    "PromotedException",
    "DemotedException",
    "PlayerExit",
    "OtherMove",
    "OtherInput",
    "NullCoordError",
]


class PromotionError(Exception):
    """Error in promotion"""
    def __init__(self, error_num=0):
        super().__init__(error_num)
        messages = [
            "Promotion error",
            "Piece is not promotable",
            "Piece is already promoted",
            "Piece is already not promoted"
        ]
        self.message = messages[error_num]

    def __str__(self): return self.message


class NotPromotableException(PromotionError):
    """Piece is not promotable."""
    def __init__(self):
        super().__init__(1)


class PromotedException(PromotionError):
    """Piece is already promoted."""
    def __init__(self):
        super().__init__(2)


class DemotedException(PromotionError):
    """Piece is already demoted."""
    def __init__(self):
        super().__init__(3)


class PlayerExit(Exception):
    """The player wishes to exit."""

class OtherMove(Exception):
    """An other move was made."""

class OtherInput(Exception):
    """A non-location input was entered."""

class NullCoordError(Exception):
    """A null coordinate was referenced."""
