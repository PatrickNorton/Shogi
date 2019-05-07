from typing import Dict, Generator, Iterable, Optional, Set, Tuple, Union

from .locations import AbsoluteCoord
from .pieces import Piece

__all__ = [
    "PieceDict",
    "CoordTuple",
    "OptCoordTuple",
    "CoordSet",
    "CoordAndSet",
    "CoordOrSet",
    "CoordIter",
    "CoordOrIter",
    "PieceDictMap",
    "CoordGen",
    "PieceDictGen",
]

PieceDict = Dict[AbsoluteCoord, Piece]
CoordTuple = Tuple[AbsoluteCoord, AbsoluteCoord]
OptCoordTuple = Tuple[Optional[AbsoluteCoord], AbsoluteCoord]
CoordSet = Set[AbsoluteCoord]
CoordAndSet = Tuple[AbsoluteCoord, CoordSet]
CoordOrSet = Union[AbsoluteCoord, Set[AbsoluteCoord]]
CoordIter = Iterable[AbsoluteCoord]
CoordOrIter = Union[AbsoluteCoord, CoordIter]
PieceDictMap = Tuple[AbsoluteCoord, Piece]
CoordGen = Generator[AbsoluteCoord, None, None]
PieceDictGen = Generator[PieceDictMap, None, None]
