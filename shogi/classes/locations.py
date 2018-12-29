from numpy import sin, cos, sign, pi

__all__ = [
    "Coord",
    "Direction"
]


class Coord:
    """A set of (x, y) coordinates.

    Attributes:
        x {int} -- the x-coordinate
        y {int} -- the y-coordinate
        TUP {tuple[int]} -- the (x, y) tuple
        XSTR {str} -- the x part of board notation
        YSTR {str} -- the y part of board notation
    """

    def __init__(self, xy):
        """Initialise instance of Coord

    Arguments:
        xy {int, str, tuple, list or Coord -- The coordinates of
            which the Coordis to be made. If xy is an integer, (x, x)
            is created.

        Raises:
            ValueError -- invalid value passed to init
        """

        if isinstance(xy, str):
            self.x = '987654321'.index(xy[1])
            self.y = 'abcdefghi'.index(xy[0])
        elif isinstance(xy, int) and abs(xy) in range(9):
            self.x = xy
            self.y = xy
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

    def __repr__(self): return f"Coord'{self}')"


class Direction(Coord):
    """A direction in which a piece moves.

    This is equivalent to a Coord with length 1, but also with an
    extra DIR attribute, which specifies the direction in which it is
    facing.

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

    def __init__(self, direction):
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

    def _make(self, xvar, yvar):
        """Turn (x, y) coordinates into a direction.

        Arguments:
            xvar {int} -- the x coordinate
            yvar {int} -- the y coordinate

        Returns:
            int -- the direction which (x, y) points
        """

        if not xvar == yvar == 0:
            return self.lis[(sign(xvar), sign(yvar))]
