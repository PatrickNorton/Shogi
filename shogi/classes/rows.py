import collections
from typing import Sequence

from .aliases import CoordGen
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
            # Add to the spaces the values in the direction of the
            # row, for as long as they are still in the board
            try:
                self.spaces.add(AbsoluteCoord(location + vector.scale(x)))
            except ValueError:
                break
        for x in RelativeCoord.negative_xy():
            # Do the same for all the values in the opposite direction
            # as what was entered, while still in the board
            try:
                self.spaces.add(AbsoluteCoord(location + vector.scale(x)))
            except ValueError:
                break

    def __iter__(self): yield from self.spaces

    def __eq__(self, other):
        if isinstance(other, Row):
            # If the first space of the other piece is in this row,
            # then make sure that their are pointing in the same
            # direction.
            # Otherwise, they aren't the same row
            if other.first_space in self:
                return (self.vector == other.vector
                        or self.vector == -1*other.vector)
            else:
                return False
        else:
            return NotImplemented

    def __repr__(self):
        return (f"{self.__class__.__name__}"
                + f"({self.first_space !r}, {self.vector !r})")

    @property
    def not_original(self) -> CoordGen:
        """Get all non-original spaces in row.

        :return: set of spaces
        """
        for space in self.spaces:
            if space != self.first_space:
                yield space
