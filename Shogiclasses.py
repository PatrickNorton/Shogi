class piece:
    def __init__(self, typ, clr):
        self.PTYPE = ptype(typ)
        self.MOVES = moves(self.NAME)
        self.COLOR = color(clr)
        self.TUP = (self.PTYPE, self.COLOR)
        self.prom = False

    def __str__(self):
        return str(self.PTYPE)+str(self.COLOR)

    def __eq__(self, other): self.TUP = other.TUP

    def __bool__(self): return not isinstance(self, nopiece)

    def promote(self):
        self.PTYPE = self.PTYPE.prom()
        self.MOVES = self.MOVES.prom()
        self.prom = True


class nopiece(piece):
    def __init__(self):
        super().__init__('-', '-')


class moves:
    with open('shogimoves.txt') as movef:
        movelist = movef.readlines()
        movedict = {}
        for line in movelist:
            movelist = movelist.split()
            movedict[movelist[0]] = movelist[1:]

    def __init__(self, piecenm):
        pcmvlist = self.movedict[piecenm]
        mvlist = pcmvlist[0]
        self.DMOVES = {direction(x): mvlist[x] for x in range(8)}
        mvlist = pcmvlist[1]
        if mvlist == 'None':
            self.PMOVES = None
        else:
            self.PMOVES = {direction(x): mvlist[x] for x in range(8)}
        self.MOVES = [self.DMOVES, self.PMOVES]
        self.ispromoted = False
        self.CMOVES = self.MOVES[self.ispromoted]

    def __getitem__(self, attr): return self.CMOVES[attr]

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


class color:
    def __init__(self, turnnum):
        self.INT = turnnum
        self.NAME = 'wb'[self.INT]
        self.OTHER = 'bw'[self.INT]

    def __str__(self): return self.STR

    def __int__(self): return self.INT

    def __eq__(self, other): return self.INT == other.INT


class ptype:
    with open('shoginames.txt') as namtxt:
        namelist = namtxt.readlines()
        for x, y in enumerate(namelist):
            namelist[x] = y.strip().split(': ')
        namedict = {x[0]: x[1] for x in namelist}

    def __init__(self, typ):
        self.TYP = typ
        self.NAME = self.namedict[self.TYP]


class direction:
    pass
