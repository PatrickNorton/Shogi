import collections

from numpy import sin, cos, sign, pi
from typing import Sequence, Union, Tuple

from .exceptions import NullCoordError

__all__ = [
    "BaseCoord",
    "RelativeCoord",
    "AbsoluteCoord",
    "Direction",
    "NullCoord"
]


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

    def __eq__(self, other): return hash(self) == hash(other)

    def __iter__(self): yield from self.tup

    def __getitem__(self, index): return self.tup[index]

    def __add__(self, other: 'BaseCoord'):
        return BaseCoord((self.x + other.x, self.y + other.y))

    def __sub__(self, other: 'BaseCoord'):
        return BaseCoord((self.x - other.x, self.y - other.y))

    def __mul__(self, other: 'BaseCoord'):
        return BaseCoord((self.x * other.x, self.y * other.y))

    def __hash__(self): return hash(self.tup)

    def __abs__(self): return AbsoluteCoord((abs(self.x), abs(self.y)))

    def __bool__(self): return not isinstance(self, NullCoord)

    def __len__(self): return len(self.tup)

    def __repr__(self): return f"BaseCoord({self})"


class RelativeCoord(BaseCoord):
    """The class for relative coordinates on the board.

    This class should be used for determining relative coordinates,
    such as for moves, and should not be used for pointing to a
    position on the board. Both the x and y coordinates must be
    in the range (-9, 9).

    If the addition or subtraction of a RelativeCoord takes the sum
    outside of the (-9, 9) range, a ValueError is raised.
    """

    def __init__(self, xy: Union[Sequence, int]):
        """Initialise instance of RelativeCoord.

        If xy is an integer, the coordinate (xy, xy) is created.

        :param xy: the coordinates of the RelativeCoord
        """
        if isinstance(xy, str):
            coordinate_tuple = (
                '987654321'.index(xy[1]),
                'abcdefghi'.index(xy[0])
            )
            super().__init__(coordinate_tuple)
        elif isinstance(xy, int) and xy in range(-8, 9):
            super().__init__((xy, xy))
        elif all(x in range(-9, 9) for x in xy):
            super().__init__(tuple(xy))
        else:
            raise ValueError(xy)

    def __add__(self, other):
        coordinates = super().__add__(other)
        return RelativeCoord(coordinates)

    def __sub__(self, other):
        coordinates = super().__sub__(other)
        return RelativeCoord(coordinates)

    def __mul__(self, other):
        coordinates = super().__mul__(other)
        return RelativeCoord(coordinates)

    def __hash__(self):
        return hash(self.tup)

    def __abs__(self):
        return RelativeCoord(super().__abs__())

    def __repr__(self):
        return f"RelativeCoord({self})"

    @staticmethod
    def same_xy():
        yield from _same_xy_rel

    @staticmethod
    def positive_xy():
        yield from _pos_xy_rel

    @staticmethod
    def negative_xy():
        return _neg_xy_rel


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

    def __init__(self, xy: Union[Sequence, int]):
        """Initialise instance of AbsoluteCoord.

        If xy is an integer, the coordinate (xy, xy) is created.

        :param xy: the coordinates of the AbsoluteCoord
        """

        if isinstance(xy, str):
            coordinate_tuple = (
                '987654321'.index(xy[1]),
                'abcdefghi'.index(xy[0])
            )
            super().__init__(coordinate_tuple)
        elif isinstance(xy, int) and xy in range(9):
            super().__init__((xy, xy))
        elif all(x in range(9) for x in xy):
            xy = (int(xy[0]), int(xy[1]))
            super().__init__(xy)
        else:
            raise ValueError(xy)
        self.x_str = '987654321'[self.x]
        self.y_str = 'abcdefghi'[self.y]

    def __str__(self):
        return self.y_str + self.x_str

    def __add__(self, other):
        coordinates = super().__add__(other)
        try:
            return AbsoluteCoord(coordinates)
        except ValueError:
            return RelativeCoord(coordinates)

    def __sub__(self, other):
        coordinates = super().__sub__(other)
        try:
            return AbsoluteCoord(coordinates)
        except ValueError:
            return RelativeCoord(coordinates)

    def __mul__(self, other):
        coordinates = super().__mul__(other)
        try:
            return AbsoluteCoord(coordinates)
        except ValueError:
            return RelativeCoord(coordinates)

    def __hash__(self):
        return hash(self.tup)

    def __abs__(self):
        return AbsoluteCoord(super().__abs__())

    def __repr__(self):
        return f"AbsoluteCoord('{self}')"

    @staticmethod
    def same_xy():
        yield from _same_xy_abs


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

    direction_set = {
        (round(sin(pi * x / 4)), -round(cos(pi * x / 4))): x for x in range(8)
    }
    inverse_directions = [
        (round(sin(pi * x / 4)), -round(cos(pi * x / 4))) for x in range(8)
    ]

    def __init__(self, direction: Union[Sequence, int]):
        self.direction: int
        if direction == (0, 0):
            self.direction = 8
        elif isinstance(direction, AbsoluteCoord):
            self.direction = self._make(direction.x, direction.y)
        elif isinstance(direction, (tuple, BaseCoord)):
            self.direction = self._make(*direction)
        elif isinstance(direction, int):
            self.direction = direction
        else:
            raise TypeError
        if self.direction != 8:
            self.tup = self.inverse_directions[self.direction]
        else:
            self.tup = (0, 0)
        super().__init__(self.tup)

    def __repr__(self):
        return f"Direction({self.direction})"

    def __abs__(self):
        return Direction(abs(self.direction))

    def __hash__(self):
        return hash(self.tup)

    @staticmethod
    def valid():
        yield from _valid_dir

    def _make(self, x_var: int, y_var: int) -> int:
        """Turn (x, y) coordinates into a direction.

        :param x_var: the x-coordinate
        :param y_var: the y coordinate
        :return: the direction in which (x, y) points
        """

        if not x_var == y_var == 0:
            return self.direction_set[(int(sign(x_var)), int(sign(y_var)))]
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

    def __repr__(self): return "NullCoord()"


_same_xy_rel = tuple(RelativeCoord(x) for x in range(-8, 9))
_pos_xy_rel = tuple(RelativeCoord(x) for x in range(9))
_neg_xy_rel = tuple(RelativeCoord(x) for x in range(0, -9, -1))

_same_xy_abs = tuple(AbsoluteCoord(x) for x in range(9))

_valid_dir = tuple(Direction(x) for x in range(8))
