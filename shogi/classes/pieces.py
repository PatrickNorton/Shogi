from .pieceattrs import Moves, Color, Ptype
from .locations import Coord
from .exceptions import (
    NotPromotableException, PromotedException, DemotedException)
from .information import info

__all__ = [
    "Piece",
    "NoPiece"
]


class Piece:
    """The class representing a piece.

    Attributes:
        PTYPE {Ptype} -- type of piece
        MOVES {Moves} -- legal moves for piece
        COLOR {Color} -- color of piece
        TUP {tuple} -- (PTYPE, COLOR)
        prom {bool or None} -- if piece is promoted
        PROMOTABLE {bool} -- if piece is promotable
        AUTOPROMOTE {int} -- where must the piece promote
    """

    def __init__(self, typ, clr):
        """Initialise instance of piece.

        Arguments:
            typ {str} -- 1-letter type of piece
            clr {str} -- 1-letter color of piece
        """

        self.PTYPE = Ptype(typ)
        self.MOVES = Moves(self.PTYPE, Color(clr))
        self.COLOR = Color(clr)
        self.TUP = (self.PTYPE, self.COLOR)
        if self.MOVES.PMOVES is None:
            self.prom = None
            self.PROMOTABLE = False
        else:
            self.prom = False
            self.PROMOTABLE = True
        otherattrs = info.PCINFO[str(typ)]
        self.AUTOPROMOTE = otherattrs['autopromote']

    def __str__(self):
        return str(self.PTYPE)+str(self.COLOR)

    def __eq__(self, other): return self.TUP == other.TUP

    def __bool__(self): return not isinstance(self, NoPiece)

    def __hash__(self): return hash(self.TUP)

    def __repr__(self): return f"{repr(self.COLOR)} {repr(self.PTYPE)}"

    def promote(self):
        """Promote piece.

        Raises:
            NotPromotableException -- piece is not promotable
            PromotedException -- piece is already promoted

        Returns:
            piece -- promoted piece
        """

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
        """Demote piece.

        Raises:
            DemotedException -- piece is not promoted

        Returns:
            piece -- demoted piece
        """

        if not self.prom:
            raise DemotedException
        else:
            self.PTYPE = self.PTYPE.dem()
            self.MOVES = self.MOVES.dem()
            self.dem = False
            return self

    def flipsides(self):
        """Change sides piece is on.

        Returns:
            piece -- flipped-color piece
        """

        return Piece(str(self.PTYPE), self.COLOR.OTHER)

    def canmove(self, relloc):
        """Check if piece can move to location.

        Arguments:
            relloc {Coord  -- relative location of move

        Returns:
            bool -- whether or not piece can move
        """

        return self.MOVES.canmove(relloc)

    def validspaces(self, direct):
        """Get spaces piece could move in a direction

        Arguments:
            direct {Direction} -- direction to be checked

        Returns:
            list -- list of valid (relative) spaces
        """

        magicvar = self.MOVES[direct]
        valid = []
        if magicvar == '-':
            return []
        elif magicvar == '1':
            valid.append(Coord(direct))
        elif magicvar == 'T':
            xy = (direct.x, 2*direct.y)
            valid.append(Coord(xy))
        elif magicvar == '+':
            for x in range(9):
                x = Coord(x)
                relloc = x*direct
                if self.canmove(relloc):
                    valid.append(relloc)
        return valid


class NoPiece(Piece):
    """The "null" instance of a piece.

    Attributes:
        PTYPE {Ptype} -- type of piece
        MOVES {Moves} -- legal moves for piece
        COLOR {Color} -- color of piece
        TUP {tuple} -- (PTYPE, COLOR)
        prom {bool or None} -- if piece is promoted
        PROMOTABLE {bool} -- if piece is promotable
        AUTOPROMOTE {int} -- where must the piece promote
    """

    def __init__(self):
        super().__init__('-', '-')

    def __repr__(self): return 'NoPiece()'
