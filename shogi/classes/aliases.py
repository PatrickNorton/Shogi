from typing import Dict, Generator, Iterable, Optional, Set, Tuple

from .locations import AbsoluteCoord
from .pieces import Piece

__all__ = [
    "PieceDict",
    "CoordTuple",
    "OptCoordTuple",
    "CoordSet",
    "CoordIter",
    "PieceDictMap",
    "CoordGen",
    "PieceDictGen",
]

PieceDict = Dict[AbsoluteCoord, Piece]
CoordTuple = Tuple[AbsoluteCoord, AbsoluteCoord]
OptCoordTuple = Tuple[Optional[AbsoluteCoord], AbsoluteCoord]
CoordSet = Set[AbsoluteCoord]
CoordIter = Iterable[AbsoluteCoord]
PieceDictMap = Tuple[AbsoluteCoord, Piece]
CoordGen = Generator[AbsoluteCoord, None, None]
PieceDictGen = Generator[PieceDictMap, None, None]
