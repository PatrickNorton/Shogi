from numpy import sin, cos, sign, pi
from .exceptions import NullCoordError
from typing import Sequence, Union, Tuple
import collections

__all__ = [
    "Coord",
    "Direction",
    "NullCoord"
]


class Coord(collections.abc.Sequence):
    """A set of (x, y) coordinates.

    These coordinates point to a position on the board, and mist be
    in the range (-9, 9) for both directions. Coordinates in the
    range(-9, -1) are for relative coordinates only and should not
    be used for pointing to a position on the board.

    :ivar x: the x coordinate
    :ivar y: the y coordinate
    :ivar tup: the (x, y) tuple
    :ivar x_str: the x part of board notation
    :ivar y_str: the y part of board notation
    """

    def __init__(self, xy: Union[Sequence, int]):
        """Initialise instance of Coord.

        If xy is an integer, the coordinate (xy, xy) is created.

        :param xy: The coordinates of the Coord
        """

        self.x: int
        self.y: int
        self.tup: Tuple[int, int]
        self.x_str: str
        self.y_str: str
        if isinstance(xy, str):
            self.x = '987654321'.index(xy[1])
            self.y = 'abcdefghi'.index(xy[0])
        elif isinstance(xy, int) and abs(xy) in range(9):
            self.x: int = xy
            self.y: int = xy
        elif all(abs(x) in range(9) for x in xy):
            self.x = int(xy[0])
            self.y = int(xy[1])
        else:
            raise ValueError(xy)
        self.tup = (self.x, self.y)
        self.x_str = '987654321'[abs(self.x)]
        self.y_str = 'abcdefghi'[abs(self.y)]

    def __str__(self): return self.y_str + self.x_str

    def __eq__(self, other): return hash(self) == hash(other)

    def __iter__(self): yield from self.tup

    def __getitem__(self, index): return self.tup[index]

    def __add__(self, other): return Coord((self.x+other.x, self.y+other.y))

    def __sub__(self, other): return Coord((self.x-other.x, self.y-other.y))

    def __mul__(self, other): return Coord((self.x*other.x, self.y*other.y))

    def __hash__(self): return hash(self.tup)

    def __abs__(self): return Coord((abs(self.x), abs(self.y)))

    def __len__(self): return len(self.tup)

    def __repr__(self): return f"Coord('{self}')"


class Direction(Coord):
    """A direction in which a piece moves.

    This is equivalent to a Coord with length 1, but also with an
    extra direction attribute, which specifies the direction in which
    it is facing. This is to be used for vectors and getting a move
    from a Moves object, where the moves are specified by direction,
    and not by absolute or relative coordinates.

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
        elif isinstance(direction, Coord):
            self.direction = self._make(direction.x, direction.y)
        elif isinstance(direction, tuple):
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

    def __repr__(self): return f"Direction({self.direction})"

    def __abs__(self): return Direction(abs(self.direction))

    def __hash__(self): return hash(self.tup)

    def _make(self, x_var: int, y_var: int) -> int:
        """Turn (x, y) coordinates into a direction.

        :param x_var: the x-coordinate
        :param y_var: the y coordinate
        :return: the direction in which (x, y) points
        """

        if not x_var == y_var == 0:
            return self.direction_set[(sign(x_var), sign(y_var))]
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
    :ivar y_str: the y part ot board notation ('-')
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

    def __repr__(self): return "NullCoord()"
