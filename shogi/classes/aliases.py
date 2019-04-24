from typing import Dict, Iterable, Optional, Set, Tuple, Union

from .locations import AbsoluteCoord
from .pieces import Piece

__all__ = [
    "PieceDict",
    "CoordTuple",
    "OptCoordTuple",
    "CoordSet",
    "CoordAndSet",
    "CoordOrSet",
    "CoordOrIter",
]

PieceDict = Dict[AbsoluteCoord, Piece]
CoordTuple = Tuple[AbsoluteCoord, AbsoluteCoord]
OptCoordTuple = Tuple[Optional[AbsoluteCoord], AbsoluteCoord]
CoordSet = Set[AbsoluteCoord]
CoordAndSet = Tuple[AbsoluteCoord, CoordSet]
CoordOrSet = Union[AbsoluteCoord, Set[AbsoluteCoord]]
CoordOrIter = Union[AbsoluteCoord, Iterable[AbsoluteCoord]]
