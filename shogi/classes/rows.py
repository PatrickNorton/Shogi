import collections
from typing import Sequence

from .aliases import CoordSet
from .locations import AbsoluteCoord, CoordLike, Direction, RelativeCoord

__all__ = [
    "Row",
]


class Row(collections.abc.Iterable):
    """The class representing a row of coordinates.

    :ivar first_space: original space added
    :ivar vector: direction of row
    :ivar spaces: set of spaces in row
    """

    def __init__(self, location: Sequence, vector: CoordLike):
        """Initialise instance of Row.

        :param location: location of original space
        :param vector: direction of row
        """

        location = AbsoluteCoord(location)
        vector = Direction(vector)
        self.first_space: AbsoluteCoord = location
        self.vector: Direction = vector
        self.spaces = set()
        for x in RelativeCoord.positive_xy():
            try:
                self.spaces.add(AbsoluteCoord(location + x * vector))
            except ValueError:
                break
        for x in RelativeCoord.negative_xy():
            try:
                self.spaces.add(AbsoluteCoord(location + x * vector))
            except ValueError:
                break
        self._not_original: CoordSet = set(
            x for x in self if x != self.first_space
        )

    def __iter__(self): yield from self.spaces

    def __eq__(self, other: 'Row') -> bool:
        if isinstance(other, Row):
            if other.first_space in self:
                return (self.vector == other.vector
                        or self.vector == -1*other.vector)
            else:
                return False
        else:
            return NotImplemented

    def __repr__(self): return f"Row({self.first_space}, {self.vector})"

    @property
    def not_original(self) -> set:
        """Get all non-original spaces in row.

        :return: set of spaces
        """

        return self._not_original
