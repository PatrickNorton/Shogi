from numpy import sin, cos, pi, sign
import os
import sys
cpath = sys.path[0]


def pathjoin(path): return os.path.join(cpath, path)


class piece:
    def __init__(self, typ, clr):
        self.PTYPE = ptype(typ)
        self.MOVES = moves(self.PTYPE, color(clr))
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

    def __eq__(self, other): return self.TUP == other.TUP

    def __bool__(self): return not isinstance(self, nopiece)

    def __hash__(self): return hash(self.TUP)

    def __repr__(self): return f"{repr(self.COLOR)} {repr(self.PTYPE)}"

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
        return piece(str(self.PTYPE), self.COLOR.OTHER)

    def canmove(self, relloc): return self.MOVES.canmove(relloc)


class nopiece(piece):
    def __init__(self):
        super().__init__('-', '-')

    def __repr__(self): return 'nopiece()'


class moves:
    with open(pathjoin('shogimoves.txt')) as movef:
        movelist = movef.readlines()
        movedict = {}
        for n, line in enumerate(movelist):
            line = line.strip()
            var = line.split(' ')
            movelist[n] = var
            movedict[line[0]] = tuple(var[1:])

    def __init__(self, piecenm, clr):
        piecenm = str(piecenm)
        pcmvlist = list(self.movedict[piecenm])
        if clr == color(1):
            for y, var in enumerate(pcmvlist):
                pcmvlist[y] = var[4:]+var[:4]
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
        dist = max(abs(relloc))
        magicvar = self[vec]
        if magicvar == '-':
            return False
        elif magicvar == '1':
            return dist == 1
        elif magicvar == '+':
            return True
        elif magicvar == 'T':
            return abs(relloc.x) == 1 and abs(relloc.y) == 2

    def prom(self):
        self.ispromoted = True
        self.CMOVES = self.MOVES[self.ispromoted]

    def dem(self):
        self.ispromoted = False
        self.CMOVES = self.MOVES[self.ispromoted]


class color:
    def __init__(self, turnnum):
        if isinstance(turnnum, int):
            self.INT = turnnum
            self.NAME = 'wb'[self.INT]
        elif isinstance(turnnum, str):
            if turnnum == '-':
                self.NAME = turnnum
                self.INT = -1
            else:
                self.NAME = turnnum
                self.INT = 'wb'.index(turnnum)
        elif isinstance(turnnum, color):
            self.INT = turnnum.INT
            self.NAME = 'wb'[self.INT]
        else:
            raise TypeError
        self.OTHER = 'bw'[self.INT]
        self.FULLNM = ['White', 'Black'][self.INT]

    def __str__(self): return self.NAME

    def __repr__(self): return self.FULLNM

    def __int__(self): return self.INT

    def __eq__(self, other): return self.INT == other.INT

    def __hash__(self): return hash((self.INT, self.NAME))

    def flip(self): return color(int(not self.INT))

    def other(self): return color(self.OTHER)


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


class NotPromotableException(Exception):
    pass


class PromotedException(Exception):
    pass


class DemotedException(Exception):
    pass


class board:
    def __init__(self, pieces=None):
        with open(pathjoin('shogiboard.txt')) as boardtxt:
            boardtxt = boardtxt.readlines()
            for x, y in enumerate(boardtxt):
                boardtxt[x] = y.split()
        if pieces is None:
            self.PIECES = {}
            for (x, y) in self.it():
                if boardtxt[y][x] != '--':
                    self.PIECES[coord((x, y))] = piece(*boardtxt[y][x])
        else:
            self.PIECES = dict(pieces)
        self.INVPIECES = {v: x for x, v in self.PIECES.items()}
        self.CAPTURED = {color(x): [] for x in range(2)}
        self.PCSBYCLR = {}
        self.currplyr = color(0)
        for x in range(2):
            theclr = color(x)
            self.PCSBYCLR[theclr] = {}
            for x, y in self.PIECES.items():
                if y.COLOR == theclr:
                    self.PCSBYCLR[theclr][x] = y
        self.lastmove = (None, None)
        self.nextmove = (None, None)

    def __str__(self):
        toreturn = ""
        captostr = [str(x) for x in self.CAPTURED[color(1)]]
        toreturn += f"Black pieces: {' '.join(captostr)}\n\n"
        toreturn += f"  {'  '.join('987654321')}\n"
        for x, var in enumerate(self):
            toreturn += f"{'abcdefghi'[x]} {' '.join(str(k) for k in var)}\n"
        captostr = [str(x) for x in self.CAPTURED[color(0)]]
        toreturn += f"White pieces: {' '.join(captostr)}\n"
        return toreturn

    def __iter__(self):
        yield from [[self[x, y] for x in range(9)] for y in range(9)]

    def __getitem__(self, index):
        if isinstance(index, (tuple, coord)):
            coords = coord(index)
            return self.PIECES.get(coords, nopiece())
        elif isinstance(index, piece):
            return self.INVPIECES[index]

    def it(self): yield from [(x, y) for x in range(9) for y in range(9)]

    def occupied(self): yield from self.PIECES

    def move(self, current, new):
        if not isinstance(self[new], nopiece):
            self.capture(new)
        self.PIECES[coord(new)] = self.PIECES.pop(current)
        self.PCSBYCLR[self[new].COLOR][coord(new)] = self[new]
        del self.PCSBYCLR[self[new].COLOR][coord(current)]

    def capture(self, new):
        piece = self[new]
        try:
            piece.demote()
        except DemotedException:
            pass
        piece = piece.flipsides()
        self.CAPTURED[self.currplyr].append(piece)
        del self.PIECES[new]
        del self.PCSBYCLR[piece.COLOR.other()][coord(new)]

    def canpromote(self, space):
        zonevar = ((0, 1, 2), (6, 7, 8))
        return space.y in zonevar[int(self.currplyr)]

    def putinplay(self, piece, movedto):
        player = self.currplyr
        if not isinstance(self[movedto], nopiece):
            raise IllegalMove(8)
        if piece.PTYPE == ptype('p'):
            rowtotest = row(movedto, 0)
            for loc in rowtotest.notoriginal():
                if self[loc] == piece('p', player):
                    raise IllegalMove(9)
        self.CAPTURED[player].remove(piece)
        self.PCSBYCLR[piece.COLOR][movedto] = piece
        self.PIECES[movedto] = piece

    def currpcs(self): return self.PCSBYCLR[self.currplyr]

    def enemypcs(self): return self.PCSBYCLR[self.currplyr.other()]

    def playerpcs(self, player): return self.PCSBYCLR[player]


class IllegalMove(Exception):
    pass


class row:
    def __init__(self, loc, vect):
        loc = coord(loc)
        vect = direction(vect)
        self.FIRSTSPACE = loc
        self.VECT = vect
        self.SPACES = set()
        for x in range(9):
            if any(y*x+z not in range(8) for y,z in zip(vect, loc)):
                break
            x = coord(x)
            self.SPACES.add(loc+x*vect)
        for x in range(0, -9, -1):
            if any(y*x+z not in range(8) for y,z in zip(vect, loc)):
                break
            x = coord(x)
            self.SPACES.add(loc+x*vect)

    def __iter__(self): yield from self.SPACES

    def __eq__(self, other):
        if isinstance(other, row):
            if other.FIRSTSPACE in self:
                return abs(self.VECT) == abs(other.VECT)
            else: return False
        else: return False

    def __repr__(self): return f"row({self.FIRSTSPACE}, {self.VECT})"

    def notoriginal(self): return (x for x in self if x != self.FIRSTSPACE)


class Shogi:
    def __init__(self):
        self.piece = piece
        self.board = board
        self.nopiece = nopiece
        self.color = color
        self.moves = moves
        self.ptype = ptype
        self.direction = direction
        self.coord = coord
        self.NotPromotableException = NotPromotableException
        self.PromotedException = PromotedException
        self.DemotedException = DemotedException
        self.IllegalMove = IllegalMove
