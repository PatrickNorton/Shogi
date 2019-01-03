from numpy import sin, cos, sign, pi
from .exceptions import NullCoordError
from typing import Sequence, Union
import collections

__all__ = [
    "Coord",
    "Direction"
]


class Coord(collections.abc.Sequence):
    """A set of (x, y) coordinates.

    These coordinates point to a position on the board, and must be
    in the range (-9, 9) for both directions. Coordinates in the
    range (-9, -1) are for relative coordinates only and should not
    be used for pointing to a position on the board.

    Attributes:
        x {int} -- the x-coordinate
        y {int} -- the y-coordinate
        TUP {tuple[int]} -- the (x, y) tuple
        XSTR {str} -- the x part of board notation
        YSTR {str} -- the y part of board notation
    """

    def __init__(self, xy: Sequence):
        """Initialise instance of Coord.

    Arguments:
        xy {int, str, tuple, list or Coord -- The coordinates of
            which the coord is to be made. If xy is an integer, (x, x)
            is created.

        Raises:
            ValueError -- invalid value passed to init
        """

        if isinstance(xy, str):
            self.x = '987654321'.index(xy[1])
            self.y = 'abcdefghi'.index(xy[0])
        elif isinstance(xy, int) and abs(xy) in range(9):  # ! Broken
            self.x: int = xy[0]
            self.y: int = xy[0]
        elif all(abs(x) in range(9) for x in xy):
            self.x = int(xy[0])
            self.y = int(xy[1])
        else:
            raise ValueError(xy)
        self.TUP = (self.x, self.y)
        self.XSTR = '987654321'[abs(self.x)]
        self.YSTR = 'abcdefghi'[abs(self.y)]

    def __str__(self): return self.YSTR+self.XSTR

    def __eq__(self, other): return hash(self) == hash(other)

    def __iter__(self): yield from self.TUP

    def __getitem__(self, index): return self.TUP[index]

    def __add__(self, other): return Coord((self.x+other.x, self.y+other.y))

    def __sub__(self, other): return Coord((self.x-other.x, self.y-other.y))

    def __mul__(self, other): return Coord((self.x*other.x, self.y*other.y))

    def __hash__(self): return hash(self.TUP)

    def __abs__(self): return Coord((abs(self.x), abs(self.y)))

    def __len__(self): return len(self.TUP)

    def __repr__(self): return f"Coord'{self}')"


class Direction(Coord):
    """A direction in which a piece moves.

    This is equivalent to a coord with length 1, but also with an
    extra DIR attribute, which specifies the direction in which it is
    facing. To be used for vectors and getting from a Moves object,
    where the moves are specified by direction, and not by absolute or
    relative coordinates.

    Attributes:
        x {int} -- the x-coordinate
        y {int} -- the y-coordinate
        TUP {tuple[int]} -- the (x, y) tuple
        XSTR {str} -- the x part of board notation
        YSTR {str} -- the y part of board notation
        DIR {int} -- which way the direction is going.
        7 0 1  Not moving is 8
        6   2
        5 4 3
    """

    lis = {(round(sin(pi*x/4)), -round(cos(pi*x/4))): x for x in range(8)}
    invlis = [(round(sin(pi*x/4)), -round(cos(pi*x/4))) for x in range(8)]

    def __init__(self, direction: Union[Sequence, int]):
        if direction == (0, 0):
            self.DIR = 8
        elif isinstance(direction, Coord):
            self.DIR = self._make(direction.x, direction.y)
        elif isinstance(direction, tuple):
            self.DIR = self._make(*direction)
        elif isinstance(direction, int):
            self.DIR = direction
        else:
            raise TypeError
        if self.DIR != 8:
            self.TUP = self.invlis[self.DIR]
        else:
            self.TUP = (0, 0)
        super().__init__(self.TUP)

    def __repr__(self): return f"Direction({self.DIR})"

    def __abs__(self): return Direction(abs(self.DIR))

    def __hash__(self): return hash(self.TUP)

    def _make(self, xvar: int, yvar: int) -> int:
        """Turn (x, y) coordinates into a direction.

        Arguments:
            xvar {int} -- the x coordinate
            yvar {int} -- the y coordinate

        Returns:
            int -- the direction which (x, y) points
        """

        if not xvar == yvar == 0:
            return self.lis[(sign(xvar), sign(yvar))]
        return 8


class NullCoord(Direction):
    """The "Null" instance of a coordinate.

    This is to be used when a coordinate does not point to any
    location on the board, such as attempting to point to the location
    of a piece which has all of its instances captured by some player.
    This inherits from Direction so that it may have a DIR attribute,
    enabling it to be used as a direction as well as a coordinate.

    Attributes:
        x {None} -- the x-coordinate (None)
        y {None} -- the y-coordinate (None)
        TUP {tuple[None]} -- the (x, y) tuple (None, None)
        XSTR {str} -- the x part of board notation ('-')
        YSTR {str} -- the y part of board notation ('-')
        DIR {int} -- which way the direction is going. (8)
    """

    def __init__(self):
        self.x = None
        self.y = None
        self.TUP = (None, None)
        self.XSTR = '-'
        self.YSTR = '-'
        self.DIR = 8

    def __eq__(self, other): return isinstance(other, NullCoord)

    def __add__(self, other): raise NullCoordError

    def __sub__(self, other): raise NullCoordError

    def __mul__(self, other): raise NullCoordError

    def __abs__(self): raise NullCoordError

    def __repr__(self): return "NullCoord()"
