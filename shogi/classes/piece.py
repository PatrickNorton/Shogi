from .ptype import ptype
from .moves import moves
from .color import color
from .coord import coord
from .exceptions import NotPromotableException, PromotedException, DemotedException
from .privates import _info

_info = _info()

__all__ = [
    "piece",
    "nopiece"
]

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
        otherattrs = _info.PCINFO[str(typ)]
        self.AUTOPROMOTE = otherattrs['autopromote']

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
            return self

    def demote(self):
        if not self.prom:
            raise DemotedException
        else:
            self.PTYPE = self.PTYPE.dem()
            self.MOVES = self.MOVES.dem()
            self.dem = False
            return self

    def flipsides(self):
        return piece(str(self.PTYPE), self.COLOR.OTHER)

    def canmove(self, relloc): return self.MOVES.canmove(relloc)

    def validspaces(self, direct):
        magicvar = self.MOVES[direct]
        valid = []
        if magicvar == '-':
            return []
        elif magicvar == '1':
            valid.append(coord(direct))
        elif magicvar == 'T':
            xy = (direct.x, 2*direct.y)
            valid.append(coord(xy))
        elif magicvar == '+':
            for x in range(9):
                x = coord(x)
                relloc = x*direct
                if self.canmove(relloc):
                    valid.append(relloc)
        return valid


class nopiece(piece):
    def __init__(self):
        super().__init__('-', '-')

    def __repr__(self): return 'nopiece()'
