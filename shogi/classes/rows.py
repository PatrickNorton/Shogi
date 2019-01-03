from .locations import Coord, Direction
from typing import Sequence, Union, Set
import collections

__all__ = [
    "Row"
]


class Row(collections.abc.Iterable):
    """The class representing a row of coordinates.

    Attributes:
        FIRSTSPACE {Coord} -- original space added
        VECT {Direction} -- direction of row
        SPACES {set} -- set of spaces in row
    """

    def __init__(self, loc: Sequence, vect: Union[Sequence, int]):
        """Initialise instance of Row.

        Arguments:
            loc {Coord} -- location of original space
            vect {Direction} -- direction of row
        """

        loc = Coord(loc)
        vect = Direction(vect)
        self.FIRSTSPACE: Coord = loc
        self.VECT: Direction = vect
        self.SPACES = set()
        for x in range(9):
            if any(y*x+z not in range(8) for y, z in zip(vect, loc)):
                break
            x = Coord(x)
            self.SPACES.add(loc+x*vect)
        for x in range(0, -9, -1):
            if any(y*x+z not in range(8) for y, z in zip(vect, loc)):
                break
            x = Coord(x)
            self.SPACES.add(loc+x*vect)
        self._notoriginal: Set[Coord] = set(x for x in self if x != self.FIRSTSPACE)

    def __iter__(self): yield from self.SPACES

    def __eq__(self, other: 'Row') -> bool:
        if isinstance(other, Row):
            if other.FIRSTSPACE in self:
                return abs(self.VECT) == abs(other.VECT)
            else:
                return False
        else:
            return False

    def __repr__(self): return f"Row({self.FIRSTSPACE}, {self.VECT})"

    @property
    def notoriginal(self) -> set:
        """Get all non-original spaces in row

        Returns:
            set -- set of spaces
        """

        return self._notoriginal
