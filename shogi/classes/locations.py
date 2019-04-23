import collections
from typing import Sequence, Tuple, Union

from .exceptions import NullCoordError

__all__ = [
    "BaseCoord",
    "RelativeCoord",
    "AbsoluteCoord",
    "Direction",
    "NullCoord",
    "CoordLike",
]


CoordLike = Union[Sequence, int]


class BaseCoord(collections.abc.Sequence):
    """The base class for coordinates.

    A BaseCoord should not be used for actual games, but instead
    should only be used as a base for inheritance.

    :ivar x: the x coordinate
    :ivar y: the y coordinate
    :ivar tup: the (x, y) tuple
    """

    def __init__(self, xy: Tuple[int, int]):
        """Initialise instance of BaseCoord.

        :param xy: the the coordinates of the AbsoluteCoord.
        """
        self.x: int = xy[0]
        self.y: int = xy[1]
        self.tup: Tuple[int, int] = xy

    def __str__(self): return str(self.tup)

    def __eq__(self, other):
        if not isinstance(other, BaseCoord):
            try:
                other = self.__class__(other)
            except TypeError:
                return NotImplemented
        return self.x == other.x and self.y == other.y

    def __iter__(self): yield from self.tup

    def __getitem__(self, index): return self.tup[index]

    def __add__(self, other: 'BaseCoord'):
        return BaseCoord(self._add(other))

    def __sub__(self, other: 'BaseCoord'):
        return BaseCoord(self._sub(other))

    def __mul__(self, other: 'BaseCoord'):
        return BaseCoord(self._mul(other))

    def __hash__(self): return hash(self.tup)

    def __abs__(self): return BaseCoord((abs(self.x), abs(self.y)))

    def __bool__(self): return not isinstance(self, NullCoord)

    def __len__(self): return len(self.tup)

    def __repr__(self): return f"{self.__class__.__name__}({self})"

    def _add(self, other: 'BaseCoord') -> Tuple[int, int]:
        return self.x + other.x, self.y + other.y

    def _sub(self, other: 'BaseCoord') -> Tuple[int, int]:
        return self.x - other.x, self.y - other.y

    def _mul(self, other: 'BaseCoord') -> Tuple[int, int]:
        return self.x * other.x, self.y * other.y

    def is_linear(self) -> bool:
        return abs(self.x) == abs(self.y) or self.x == 0 or self.y == 0


class RelativeCoord(BaseCoord):
    """The class for relative coordinates on the board.

    This class should be used for determining relative coordinates,
    such as for moves, and should not be used for pointing to a
    position on the board. Both the x and y coordinates must be
    in the range (-9, 9).

    If the addition or subtraction of a RelativeCoord takes the sum
    outside of the (-9, 9) range, a ValueError is raised.
    """

    def __init__(self, xy: CoordLike):
        """Initialise instance of RelativeCoord.

        If xy is an integer, the coordinate (xy, xy) is created.

        :param xy: the coordinates of the RelativeCoord
        """
        # Turn an integer input into a coordinate
        if isinstance(xy, int) and xy in range(-8, 9):
            super().__init__((xy, xy))
        # Otherwise, use the iterable to turn it into a RelCoord
        elif all(x in range(-8, 9) for x in xy):
            super().__init__(tuple(xy))
        else:
            raise ValueError(f"{xy} not in correct range")

    def __add__(self, other: CoordLike):
        if not isinstance(other, BaseCoord):
            other = RelativeCoord(other)
        return RelativeCoord(self._add(other))

    def __sub__(self, other: CoordLike):
        if not isinstance(other, BaseCoord):
            other = RelativeCoord(other)
        return RelativeCoord(self._sub(other))

    def __mul__(self, other: CoordLike):
        if not isinstance(other, BaseCoord):
            other = RelativeCoord(other)
        return RelativeCoord(self._mul(other))

    def __hash__(self):
        return hash(self.tup)

    def __abs__(self):
        return RelativeCoord(super().__abs__())

    @staticmethod
    def same_xy():
        for x in range(-8, 9):
            yield RelativeCoord(x)

    @staticmethod
    def positive_xy():
        for x in range(1, 9):
            yield RelativeCoord(x)

    @staticmethod
    def negative_xy():
        for x in range(0, -9, -1):
            yield RelativeCoord(x)


class AbsoluteCoord(BaseCoord):
    """A set of (x, y) coordinates.

    These coordinates point to a position on the board, and must be
    in the range (0, 9) for both directions. This coordinate should
    be used for pointing at locations on the board.

    If the addition or subtraction of an AbsoluteCoord takes it out
    of the (0, 9) range, a RelativeCoord is instead returned.

    :ivar x_str: the x part of board notation
    :ivar y_str: the y part of board notation
    """

    def __init__(self, xy: CoordLike):
        """Initialise instance of AbsoluteCoord.

        If xy is an integer, the coordinate (xy, xy) is created.

        :param xy: the coordinates of the AbsoluteCoord
        """

        # Handle string inputs
        if isinstance(xy, str):
            coordinate_tuple = (
                '123456789'.index(xy[1]),
                8 - 'abcdefghi'.index(xy[0])
            )
            super().__init__(coordinate_tuple)
        # Handle integer inputs
        elif isinstance(xy, int) and xy in range(9):
            super().__init__((xy, xy))
        # Handle iterable inputs
        elif all(x in range(9) for x in xy):
            xy = (int(xy[0]), int(xy[1]))
            super().__init__(xy)
        else:
            raise ValueError(f"{xy} not in correct range")
        self.x_str = '123456789'[self.x]
        self.y_str = 'abcdefghi'[::-1][self.y]

    def __str__(self):
        return self.y_str + self.x_str

    def __add__(self, other):
        if not isinstance(other, BaseCoord):
            other = AbsoluteCoord(other)
        coordinates = self._add(other)
        try:
            return AbsoluteCoord(coordinates)
        except ValueError:
            return RelativeCoord(coordinates)

    def __sub__(self, other):
        if not isinstance(other, BaseCoord):
            other = AbsoluteCoord(other)
        coordinates = self._sub(other)
        try:
            return AbsoluteCoord(coordinates)
        except ValueError:
            return RelativeCoord(coordinates)

    def __mul__(self, other):
        if not isinstance(other, BaseCoord):
            other = AbsoluteCoord(other)
        coordinates = self._mul(other)
        try:
            return AbsoluteCoord(coordinates)
        except ValueError:
            return RelativeCoord(coordinates)

    def __hash__(self):
        return hash(self.tup)

    def __abs__(self):
        return AbsoluteCoord(super().__abs__())

    def __repr__(self):
        return f"{self.__class__.__name__}('{self}')"

    @staticmethod
    def same_xy():
        for x in range(-8, 9):
            yield RelativeCoord(x)


def _sign(x): return int(x > 0) - int(x < 0)


class Direction(RelativeCoord):
    """A direction in which a piece moves.

    This is equivalent to a AbsoluteCoord with length 1, but also
    with an extra direction attribute, which specifies the direction
    in which it is facing. This is to be used for vectors and getting
    a move from a Moves object, where the moves are specified by
    direction, and not by absolute or relative coordinates.

    Directions:

    7 0 1   Not moving is direction 8
    6   2
    5 4 3

    :ivar direction: which way the direction is facing
    :cvar direction_set: maps coordinate pair to direction number
    :cvar inverse_directions: inverse of direction_set
    """

    direction_set = {(0, -1): 0, (1, -1): 1, (1, 0): 2, (1, 1): 3,
                     (0, 1): 4, (-1, 1): 5, (-1, 0): 6, (-1, -1): 7}
    inverse_directions = [(0, -1), (1, -1), (1, 0), (1, 1),
                          (0, 1), (-1, 1), (-1, 0), (-1, -1)]

    def __init__(self, direction: CoordLike):
        self.direction: int
        # If the null direction ins entered:
        if direction == (0, 0):
            self.direction = 8
        # If direction is a coordinate pair, -> self.tup
        elif isinstance(direction, (tuple, BaseCoord)):
            self.direction = self._make(*direction)
        # If it's an int, then direction -> self.direction
        elif isinstance(direction, int):
            self.direction = direction
        else:
            raise TypeError
        if self.direction != 8:
            self.tup = self.inverse_directions[self.direction]
        else:
            self.tup = (0, 0)
        super().__init__(self.tup)

    def __abs__(self):
        return Direction(abs(self.direction))

    def __hash__(self):
        return hash(self.tup)

    @staticmethod
    def valid():
        for x in range(8):
            yield Direction(x)

    def _make(self, x_var: int, y_var: int) -> int:
        """Turn (x, y) coordinates into a direction.

        :param x_var: the x-coordinate
        :param y_var: the y coordinate
        :return: the direction in which (x, y) points
        """

        if not x_var == y_var == 0:
            return self.direction_set[(_sign(x_var), _sign(y_var))]
        return 8


class NullCoord(Direction):
    """The "Null" instance of a coordinate.

    This is to be used when a coordinate does not point to any
    location on the board, such as attempting to point to the
    location of a piece which has all of its instances captured by
    some player. This inherits from Direction so that it may have a
    direction attribute, enabling it to be used as a direction as
    well as a coordinate.

    :ivar x: the x-coordinate (None)
    :ivar y: the y-coordinate (None)
    :ivar tup: the (x, y) tuple (None, None)
    :ivar x_str: the x part of board notation ('-')
    :ivar y_str: the y part of board notation ('-')
    """

    def __init__(self):
        """Initialise instance of NullCoord.

        """
        super().__init__(8)
        self.x = None
        self.y = None
        self.tup = (None, None)
        self.x_str = '-'
        self.y_str = '-'

    def __eq__(self, other): return isinstance(other, NullCoord)

    def __add__(self, other): raise NullCoordError

    def __sub__(self, other): raise NullCoordError

    def __mul__(self, other): raise NullCoordError

    def __abs__(self): raise NullCoordError

    def __hash__(self): return hash(self.tup)

    def __repr__(self): return f"{self.__class__.__name__}()"

    @staticmethod
    def valid():
        yield NullCoord()
