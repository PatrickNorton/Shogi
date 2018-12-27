from .locations import direction
from .privates import _info

__all__ = [
    "color",
    "ptype",
    "moves"
]


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
    def __init__(self, typ):
        typ = str(typ)
        self.TYP = typ.lower()
        self.NAME = _info.NAMEDICT[self.TYP]

    def __str__(self): return self.TYP

    def __repr__(self): return self.NAME

    def __eq__(self, other): return repr(self) == repr(other)

    def __hash__(self): return hash((self.TYP, self.NAME))

    def prom(self):
        self.TYP = self.TYP.upper()
        self.NAME = '+'+self.NAME
        return self

    def dem(self):
        self.TYP = self.TYP.lower()
        self.NAME = self.NAME.replace('+', '')
        return self


class moves:
    def __init__(self, piecenm, clr):
        piecenm = str(piecenm)
        pcmvlist = list(_info.MOVEDICT[piecenm])
        if clr == color(1):
            for y, var in enumerate(pcmvlist):
                if var is not None:
                    pcmvlist[y] = var[4:]+var[:4]
        mvlist = pcmvlist[0]
        self.DMOVES = {direction(x): mvlist[x] for x in range(8)}
        self.DMOVES[direction(8)] = '-'
        mvlist = pcmvlist[1]
        if mvlist is None:
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
        return self

    def dem(self):
        self.ispromoted = False
        self.CMOVES = self.MOVES[self.ispromoted]
        return self
