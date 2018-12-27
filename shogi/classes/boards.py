from .locations import coord
from .pieces import piece, nopiece
from .pieceattrs import color, ptype
from .privates import _info
from .exceptions import PromotedException, DemotedException, IllegalMove
from .rows import row

__all__ = [
    "board"
]

class board:
    def __init__(self, pieces=None):
        if pieces is None:
            self.PIECES = {coord(x): piece(*y) for x, y in _info.LS.items()}
        else:
            self.PIECES = dict(pieces)
        self.INVPIECES = {v: x for x, v in self.PIECES.items()}
        self.CAPTURED = {color(x): [] for x in range(2)}
        self.PCSBYCLR = {color(0): {}, color(1): {}}
        self.currplyr = color(0)
        for x in range(2):
            theclr = color(x)
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
        toreturn += f"White pieces: {' '.join(captostr)}\n\n"
        return toreturn

    def __iter__(self):
        yield from ([self[x, y] for x in range(9)] for y in range(9))

    def __getitem__(self, index):
        coords = coord(index)
        toreturn = self.PIECES.get(coords, nopiece())
        return toreturn

    def it(self): yield from ((x, y) for x in range(9) for y in range(9))

    def occupied(self): yield from self.PIECES

    def move(self, current, new):
        if not isinstance(self[new], nopiece):
            self.capture(new)
        self.PIECES[coord(new)] = self.PIECES.pop(current)
        self.PCSBYCLR[self[new].COLOR][coord(new)] = self[new]
        del self.PCSBYCLR[self[new].COLOR][coord(current)]
        self.INVPIECES[self[new]] = new

    def getpiece(self, location):
        return self.INVPIECES[location]

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
        if piece in self.PIECES:
            gen = [loc for loc, x in self.PIECES.items() if x == piece]
            self.INVPIECES[piece] = gen[0]
        else:
            del self.INVPIECES[piece]

    def canpromote(self, space):
        zonevar = ((0, 1, 2), (8, 7, 6))
        return space.y in zonevar[int(self.currplyr)]

    def autopromote(self, space):
        zonevar = ((0, 1, 2), (8, 7, 6))
        plyrint = int(self.currplyr)
        index = zonevar[plyrint].index(space.y)
        return index < self[space].AUTOPROMOTE

    def promote(self, space):
        piece = self[space]
        piece = piece.promote()
        self.PIECES[space] = piece
        self.PCSBYCLR[piece.COLOR][space] = piece
        self.INVPIECES[piece] = space

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
        self.INVPIECES[piece] = movedto

    def currpcs(self): return self.PCSBYCLR[self.currplyr]

    def enemypcs(self): return self.PCSBYCLR[self.currplyr.other()]

    def playerpcs(self, player): return self.PCSBYCLR[player]
