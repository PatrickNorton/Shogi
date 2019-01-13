import collections

from typing import Sequence, Union, Set

from .locations import AbsoluteCoord, Direction, RelativeCoord

__all__ = [
    "Row"
]


class Row(collections.abc.Iterable):
    """The class representing a row of coordinates.

    :ivar first_space: original space added
    :ivar vector: direction of row
    :ivar spaces: set of spaces in row
    """

    def __init__(self, location: Sequence, vector: Union[Sequence, int]):
        """Initialise instance of Row.

        :param location: location of original space
        :param vector: direction of row
        """

        location = AbsoluteCoord(location)
        vector = Direction(vector)
        self.first_space: AbsoluteCoord = location
        self.vector: Direction = vector
        self.spaces = set()
        for x in range(9):
            if any(y*x+z not in range(8) for y, z in zip(vector, location)):
                break
            x = RelativeCoord(x)
            self.spaces.add(AbsoluteCoord(location + x * vector))
        for x in range(0, -9, -1):
            if any(y*x+z not in range(8) for y, z in zip(vector, location)):
                break
            x = RelativeCoord(x)
            self.spaces.add(AbsoluteCoord(location + x * vector))
        self._not_original: Set[AbsoluteCoord] = set(x for x in self if x != self.first_space)

    def __iter__(self): yield from self.spaces

    def __eq__(self, other: 'Row') -> bool:
        if isinstance(other, Row):
            if other.first_space in self:
                return abs(self.vector) == abs(other.vector)
            else:
                return False
        else:
            return False

    def __repr__(self): return f"Row({self.first_space}, {self.vector})"

    @property
    def not_original(self) -> set:
        """Get all non-original spaces in row.

        :return: set of spaces
        """

        return self._not_original
