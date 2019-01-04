from .pieceattrs import Moves, Color, Ptype
from .locations import Coord, Direction
from .exceptions import (
    NotPromotableException, PromotedException, DemotedException)
from .information import info
from typing import Tuple, Optional, List, Union

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

    def __init__(self, typ: str, clr: str):
        """Initialise instance of piece.

        Arguments:
            typ {str} -- 1-letter type of piece
            clr {str} -- 1-letter color of piece
        """

        self.PTYPE: Ptype = Ptype(typ)
        self.MOVES: Moves = Moves(self.PTYPE, Color(clr))
        self.COLOR: Color = Color(clr)
        self.TUP: Tuple[Ptype, Color] = (self.PTYPE, self.COLOR)
        self.prom: Optional[bool]
        self.PROMOTABLE: bool
        if self.MOVES.PMOVES is None:
            self.prom = None
            self.PROMOTABLE = False
        else:
            self.prom = False
            self.PROMOTABLE = True
        otherattrs: dict = info.PCINFO[str(typ)]
        self.AUTOPROMOTE: int = otherattrs['autopromote']

    def __str__(self):
        return str(self.PTYPE)+str(self.COLOR)

    def __eq__(self, other: 'Piece') -> bool: return self.TUP == other.TUP

    def __bool__(self): return not isinstance(self, NoPiece)

    def __hash__(self): return hash(self.TUP)

    def __repr__(self): return f"{self.COLOR !r} {self.PTYPE !r}"

    def promote(self) -> 'Piece':
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

    def demote(self) -> 'Piece':
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
            self.prom = False
            return self

    def flipsides(self) -> 'Piece':
        """Change sides piece is on.

        Returns:
            piece -- flipped-color piece
        """

        return Piece(str(self.PTYPE), self.COLOR.OTHER)

    def canmove(self, relloc: Coord) -> bool:
        """Check if piece can move to location.

        Arguments:
            relloc {Coord}  -- relative location of move

        Returns:
            bool -- whether or not piece can move
        """

        return self.MOVES.canmove(relloc)

    def validspaces(self, direct: Direction) -> List[Coord]:
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

    def samecolor(self, other: 'Piece') -> bool:
        """Check if piece has the same color as another piece.

        Arguments:
            other {Piece} -- the piece to be compared

        Returns:
            bool -- if they have the same color
        """

        return self.COLOR == other.COLOR

    def sametype(self, other: 'Piece') -> bool:
        """Check if piece is the same type as another piece.

        Arguments:
            other {Piece} -- the piece to be compared

        Returns:
            bool -- if they are the same type
        """

        return self.PTYPE == other.PTYPE

    def iscolor(self, clr: Union[Color, int, str]) -> bool:
        """Check if piece is of a certain color.

        This can take either a color, an int or a str object. It
        should be used as a replacement for "instance.COLOR ==
        Color('x')", as that is more verbose than necessary.

        Arguments:
            clr {Color, int or str} -- color to be tested

        Returns:
            bool -- if the piece is of that color
        """

        if isinstance(clr, Color):
            return self.COLOR == clr
        elif isinstance(clr, str):
            return str(self.COLOR) == clr
        elif isinstance(clr, int):
            return int(self.COLOR) == clr
        return False

    def hastype(self, typ: Union[Ptype, str]) -> bool:
        """Check if piece is of a certain type.

        This can take either a ptype or a str object. It should be
        used as a replacement for "instance.PTYPE == Ptype('x')", as
        that is more verbose than necessary.

        Arguments:
            typ {Ptype or str} -- type to be tested

        Returns:
            bool -- if the piece is of that type
        """

        if isinstance(typ, Ptype):
            return self.PTYPE == typ
        elif isinstance(typ, str):
            return str(self.PTYPE) == typ
        return False

    def ispiece(self,
                typ: Union[Ptype, str],
                clr: Union[Color, int, str]
                ) -> bool:
        """Check if the piece of a certain color and type.

        Arguments:
            typ {Ptype or str} -- type to check
            clr {Color, int, or str} -- color to check

        Returns:
            bool -- if the piece is of the same type and color
        """

        return self.hastype(typ) and self.iscolor(clr)


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
