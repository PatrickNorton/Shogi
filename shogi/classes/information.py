from .privates import _InfoClass

__all__ = [
    "info"
]

info: _InfoClass = _InfoClass()
"""The instance of Piece to be used. Contains all data."""
