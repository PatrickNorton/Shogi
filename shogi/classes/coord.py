from numpy import sin, cos, sign, pi

__all__ = [
    "coord",
    "direction"
]

class coord:
    def __init__(self, xy):
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

    def __add__(self, other): return coord((self.x+other.x, self.y+other.y))

    def __sub__(self, other): return coord((self.x-other.x, self.y-other.y))

    def __mul__(self, other): return coord((self.x*other.x, self.y*other.y))

    def __hash__(self): return hash(self.TUP)

    def __abs__(self): return coord((abs(self.x), abs(self.y)))

    def __repr__(self): return f"coord('{self}')"


class direction(coord):
    lis = {(round(sin(pi*x/4)), -round(cos(pi*x/4))): x for x in range(8)}
    invlis = [(round(sin(pi*x/4)), -round(cos(pi*x/4))) for x in range(8)]

    def __init__(self, direction):
        if direction == (0, 0):
            self.DIR = 8
        elif isinstance(direction, coord):
            self.DIR = self.make(direction.x, direction.y)
        elif isinstance(direction, tuple):
            self.DIR = self.make(*direction)
        elif isinstance(direction, int):
            self.DIR = direction
        else:
            raise TypeError
        if self.DIR != 8:
            self.TUP = self.invlis[self.DIR]
        else:
            self.TUP = (0, 0)
        super().__init__(self.TUP)

    def __repr__(self): return f"direction({self.DIR})"

    def __abs__(self): return direction(abs(self.DIR))

    def __hash__(self): return hash(self.TUP)

    def make(self, xvar, yvar):
        if not xvar == yvar == 0:
            return self.lis[(sign(xvar), sign(yvar))]
