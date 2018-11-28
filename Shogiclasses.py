from numpy import sin, cos, pi
import os
import sys
cpath = sys.path[0]


def pathjoin(path): return os.path.join(cpath, path)


class piece:
    def __init__(self, typ, clr):
        self.PTYPE = ptype(typ)
        self.MOVES = moves(self.NAME, color(clr))
        self.COLOR = color(clr)
        self.TUP = (self.PTYPE, self.COLOR)
        if self.MOVES.PMOVES is None:
            self.prom = None
            self.PROMOTABLE = False
        else:
            self.prom = False
            self.PROMOTABLE = True

    def __str__(self):
        return str(self.PTYPE)+str(self.COLOR)

    def __eq__(self, other): self.TUP = other.TUP

    def __bool__(self): return not isinstance(self, nopiece)

    def __hash__(self): return hash(self.TUP)

    def promote(self):
        if self.prom is None:
            raise NotPromotableException
        elif self.prom:
            raise PromotedException
        else:
            self.PTYPE = self.PTYPE.prom()
            self.MOVES = self.MOVES.prom()
            self.prom = True

    def demote(self):
        if not self.prom:
            raise DemotedException
        else:
            self.PTYPE = self.PTYPE.dem()
            self.MOVES = self.MOVES.dem()

    def flipsides(self):
        self.COLOR = color(self.COLOR.OTHER)

    def canmove(self, relloc): return self.MOVES.canmove(relloc)


class nopiece(piece):
    def __init__(self):
        super().__init__('-', '-')


class moves:
    with open(pathjoin('shogimoves.txt')) as movef:
        movelist = movef.readlines()
        movedict = {}
        for n, line in enumerate(movelist):
            movelist[n] = line.split()
            movedict[line[0]] = line[1:]

    def __init__(self, piecenm, clr):
        piecenm = str(piecenm)
        pcmvlist = self.movedict[piecenm]
        if clr == color(1):
            pcmvlist = [x[::-1] for x in pcmvlist]
        mvlist = pcmvlist[0]
        self.DMOVES = {direction(x): mvlist[x] for x in range(8)}
        self.DMOVES[direction(8)] = '-'
        mvlist = pcmvlist[1]
        if mvlist in ('None', 'enoN'):
            self.PMOVES = None
        else:
            self.PMOVES = {direction(x): mvlist[x] for x in range(8)}
            self.PMOVES[direction(8)] = '-'
        self.MOVES = [self.DMOVES, self.PMOVES]
        self.ispromoted = False
        self.CMOVES = self.MOVES[self.ispromoted]

    def __getitem__(self, attr): return self.CMOVES[attr]

    def __iter__(self): yield from self.CMOVES

    def canmove(self, relloc):  # Takes coord object
        vec = direction(relloc)
        dist = max(relloc)
        if self[vec] == '-':
            return False
        elif self[vec] == '1':
            return dist == 1
        elif self[vec] == '+':
            return True
        elif self[vec] == 'T':
            return abs(relloc.x) == 1 and relloc.y == 2

    def prom(self):
        self.ispromoted = True
        self.CMOVES = self.MOVES[self.ispromoted]

    def dem(self):
        self.ispromoted = False
        self.CMOVES = self.MOVES[self.ispromoted]


class color:
    def __init__(self, turnnum):
        self.INT = turnnum
        self.NAME = 'wb'[self.INT]
        self.OTHER = 'bw'[self.INT]
        self.FULLNM = ['White', 'Black'][self.INT]

    def __str__(self): return self.NAME

    def __repr__(self): return self.FULLNM

    def __int__(self): return self.INT

    def __eq__(self, other): return self.INT == other.INT

    def __hash__(self): return hash((self.INT, self.NAME))

    def flip(self): return color(int(not self.INT))


class ptype:
    with open(pathjoin('shoginames.txt')) as namtxt:
        namelist = namtxt.readlines()
        for x, y in enumerate(namelist):
            namelist[x] = y.strip().split(': ')
        namedict = {x[0]: x[1] for x in namelist}

    def __init__(self, typ):
        typ = str(typ)
        self.TYP = typ.lower()
        self.NAME = self.namedict[self.TYP]

    def __str__(self): return self.TYP

    def __repr__(self): return self.NAME

    def __eq__(self, other): return repr(self) == repr(other)

    def __hash__(self): return hash((self.TYP, self.NAME))

    def prom(self):
        self.TYP = self.TYP.upper()
        self.NAME = '+'+self.NAME

    def dem(self):
        self.TYP = self.TYP.lower()
        self.NAME = self.NAME.replace('+', '')


class direction:
    lis = {(round(sin(pi*x/4)), round(cos(pi*x/4))): x for x in range(8)}
    invlis = [(round(sin(pi*x/4)), round(cos(pi*x/4))) for x in range(8)]

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

    def __eq__(self, other): return self.DIR == other.DIR

    def __iter__(self): yield from self.TUP

    def __getitem__(self, index): return self.TUP[index]

    def make(self, xvar, yvar):
        if not xvar == yvar == 0:
            self.DIR = self.lis[(xvar, yvar)]


class coord:
    def __init__(self, xy):
        if isinstance(xy, str):
            self.x = 'abcdefghi'.index(xy[0])
            self.y = '987654321'.index(xy[1])
        elif all(x in range(9) for x in xy):
            self.x = xy[0]
            self.y = xy[1]
        else:
            raise ValueError
        self.TUP = (self.x, self.y)

    def __eq__(self, other): return hash(self) == hash(other)

    def __iter__(self): yield from self.TUP

    def __getitem__(self, index): return self.TUP[index]

    def __add__(self, other): return coord((self.x+other.x, self.y+other.y))

    def __sub__(self, other): return coord((self.x-other.x, self.y-other.y))

    def __mul__(self, other): return coord((self.x*other.x, self.y*other.y))

    def __hash__(self): return hash(self.TUP)

    def __abs__(self): return coord((abs(self.x), abs(self.y)))


class NotPromotableException(Exception):
    pass


class PromotedException(Exception):
    pass


class DemotedException(Exception):
    pass


class board:
    def __init__(self):
        with open(pathjoin('shogiboard.txt')) as boardtxt:
            boardtxt = boardtxt.readlines()
            for x, y in enumerate(boardtxt):
                boardtxt[x] = y.split()
        self.PIECES = {}
        for (x, y) in self.it():
            if boardtxt[y][x] != '--':
                self.PIECES[coord((x, y))] = piece(*boardtxt[y][x])
        self.INVPIECES = {v: x for x, v in self.PIECES.items()}
        self.CAPTURED = {color(x): [] for x in range(1)}
        self.PCSBYCLR = {}
        for x in range(1):
            theclr = color(x)
            self.PCSBYCLR[theclr] = {}
            for x, y in enumerate(self.PIECES):
                if y.COLOR == self.currplyr:
                    self.PCSBYCLR[theclr][x] = y
        self.currplyr = color(0)

    def __str__(self):
        toreturn = ""
        toreturn += f"Black pieces: {' '.join(self.CAPTURED[color(1)])}"
        toreturn += '  '.join('987654321')+'\n'
        for x, var in enumerate(self):
            toreturn += f"{'abcdefghi'[x]}{' '.join(str(x))}\n"
        toreturn += f"White pieces: {' '.join(self.CAPTURED[color(1)])}"
        return toreturn

    def __iter__(self):
        yield from [[self[x, y] for x in range(9)] for y in range(9)]

    def __getitem__(self, index):
        if isinstance(index, (tuple, coord)):
            coords = coord(index)
            return self.PIECES.get(coords, nopiece())
        elif isinstance(index, piece):
            return self.INVPIECES.get(index)

    def it(self): yield from [(x, y) for x in range(9) for y in range(9)]

    def occupied(self): yield from self.PIECES

    def move(self, current, new):
        if not isinstance(self[new], nopiece):
            self.capture(new)
        self.PIECES[coord(new)] = self.PIECES.pop(current)

    def capture(self, new):
        piece = self[new]
        piece.demote()
        piece.flipsides()
        self.captured[self.currplyr] = piece
        del self.PIECES[new]

    def canpromote(self, space):
        zonevar = [[6, 7, 8], [0, 1, 2]]
        return space.y in zonevar[int(board.currplyr)]

    def putinplay(self, piece, movedto):
        player = self.currplyr
        self.CAPTURED[player].remove(piece)
        if not isinstance(self[movedto], nopiece):
            raise IllegalMove

    def playerpcs(self): yield from self.PCSBYCLR[self.currplyr]

    def enemypcs(self): yield from self.PCSBYCLR[self.currplyr.other()]


class IllegalMove(Exception):
    pass
