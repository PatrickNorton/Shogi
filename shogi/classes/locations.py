import collections
import itertools
from typing import Sequence, Tuple, Union, Iterable

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
        if not (isinstance(xy, tuple) and all(isinstance(i, int) for i in xy)):
            raise TypeError(f"Expected {Tuple[int, int]}, got {type(xy)}.")
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

    def __add__(self, other):
        if not isinstance(other, BaseCoord):
            try:
                other = self.__class__(other)
            except TypeError:
                return NotImplemented
        return self.__class__((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        if not isinstance(other, BaseCoord):
            try:
                other = self.__class__(other)
            except TypeError:
                return NotImplemented
        return self.__class__((self.x - other.x, self.y - other.y))

    def __mul__(self, other):
        if not isinstance(other, BaseCoord):
            try:
                other = self.__class__(other)
            except TypeError:
                return NotImplemented
        return self.__class__((self.x * other.x, self.y * other.y))

    def __abs__(self): return self.__class__((abs(self.x), abs(self.y)))

    def __hash__(self): return hash(self.tup)

    def __bool__(self): return not isinstance(self, NullCoord)

    def __len__(self): return len(self.tup)

    def __repr__(self): return f"{self.__class__.__name__}({self.tup !r})"

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
        if isinstance(xy, int):
            if xy in range(-8, 9):
                super().__init__((xy, xy))
            else:
                raise ValueError(f"{xy} not in correct range")
        # Otherwise, use the iterable to turn it into a RelCoord
        elif isinstance(xy, Iterable):
            if all(x in range(-8, 9) for x in xy):
                super().__init__(tuple(xy))
            else:
                raise ValueError(f"{xy} not in correct range")
        else:
            raise TypeError(f"Expected {CoordLike}, got {type(xy)}.")

    @classmethod
    def same_xy(cls):
        """All pieces with the same x and y coordinate."""
        for x in range(-8, 9):
            yield cls(x)

    @classmethod
    def positive_xy(cls):
        """All pieces within same_xy with a positive coordinate."""
        for x in range(1, 9):
            yield cls(x)

    @classmethod
    def negative_xy(cls):
        """Same as positive_xy, but negative coordinates."""
        for x in range(-1, -9, -1):
            yield cls(x)

    @classmethod
    def one_away(cls):
        """All the relative locations with a max value of 1. """
        for x in itertools.product((-1, 0, 1), repeat=2):
            if x != (0, 0):
                yield cls(x)


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
        elif isinstance(xy, int):
            if xy in range(9):
                super().__init__((xy, xy))
            else:
                raise ValueError(f"{xy} not in correct range")
        # Handle iterable inputs
        elif isinstance(xy, Iterable):
            if all(x in range(9) for x in xy):
                super().__init__(tuple(xy))
            else:
                raise ValueError(f"{xy} not in correct range")
        else:
            raise TypeError(f"Expected {CoordLike}, got {type(xy)}")
        self.x_str = '123456789'[self.x]
        self.y_str = 'abcdefghi'[::-1][self.y]

    def __str__(self):
        return self.y_str + self.x_str

    def __repr__(self):
        return f"{self.__class__.__name__}({self.y_str + self.x_str !r})"

    @staticmethod
    def same_xy():
        for x in range(-8, 9):
            yield RelativeCoord(x)

    def distance_to(self, other: 'AbsoluteCoord') -> RelativeCoord:
        """Get the distance to the other coordinate.

        This was created in response to the removal of automatic
        type conversion to RelativeCoord when subtracting and adding
        AbsoluteCoords formerly.
        This finds the number of spaces needed to move in each
        direction _from_ self _to_ other, for example,
            (0, 0).distance_to((1, 0)) => (1, 0)

        :param other: The coordinate whose distance we are finding
        :return: The distance to the other coordinate
        """
        return RelativeCoord((other.x - self.x, other.y - self.y))


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
                     (0, 1): 4, (-1, 1): 5, (-1, 0): 6, (-1, -1): 7,
                     (0, 0): 8}
    inverse_directions = [(0, -1), (1, -1), (1, 0), (1, 1),
                          (0, 1), (-1, 1), (-1, 0), (-1, -1),
                          (0, 0)]

    def __init__(self, direction: CoordLike):
        self.direction: int
        # If direction is a coordinate pair, -> self.tup
        if isinstance(direction, (tuple, BaseCoord)):
            self.direction = self._make(*direction)
        # If it's an int, then direction -> self.direction
        elif isinstance(direction, int):
            self.direction = direction
        else:
            raise TypeError(
                f"Expected {CoordLike}, got {type(direction)}"
            )
        super().__init__(self.inverse_directions[self.direction])

    @staticmethod
    def valid():
        for x in range(8):
            yield Direction(x)

    def scale(self, scalar: CoordLike) -> RelativeCoord:
        """Scale a coordinate in a direction.

        This is to be used for things like moving a certain number of
        spaces in one direction or another, where writing out
            RelativeCoord(x) * direction_of_movement
        can get pretty tedious pretty quickly, as well as quite long.

        :param scalar: coordinate to scale
        :return: the scaled coordinate
        """
        if not isinstance(scalar, BaseCoord):
            try:
                scalar = RelativeCoord(scalar)
            except TypeError:
                raise TypeError
        return RelativeCoord((self.x * scalar.x, self.y * scalar.y))

    def _make(self, x_var: int, y_var: int) -> int:
        """Turn (x, y) coordinates into a direction.

        :param x_var: the x-coordinate
        :param y_var: the y coordinate
        :return: the direction in which (x, y) points
        """

        return self.direction_set[(_sign(x_var), _sign(y_var))]


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

    def __repr__(self): return f"{self.__class__.__name__}()"

    @classmethod
    def valid(cls):
        yield cls()
