from .exceptions import PromotedException, NotPromotableException
from .exceptions import DemotedException
from .locations import Direction, Coord
from .information import info
from typing import Union, Dict, Optional, Generator
import collections

__all__ = [
    "Color",
    "Ptype",
    "Moves"
]


class Color:
    """The class for piece/player colors.

    This class is used both for the color of a player (e.g. the Board
    object's currplyr attribute being an instance of Color), and the
    color of a piece (e.g. the Piece.COLOR attribute being a Color).
    This class is what should be used for comparisons between two
    piece's colors.

    Attributes:
        INT {int} -- the integer (white=0, black=1) of the turn
        NAME {str} -- the character (w, b) of the color
        OTHER {str} -- the character of the other color
        FULLNM {str} -- the full name (White, Black) of the color
    """


    def __init__(self, turnnum: Union[int, str, 'Color']):
        """Initialise instance of Color.

        Arguments:
            turnnum {str or int} -- piece's color (w/b or 0/1)

        Raises:
            TypeError -- invalid type
        """
        self.INT: int
        self.NAME: str
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
        elif isinstance(turnnum, Color):
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

    @property
    def other(self) -> 'Color':
        """Color: Opposite color from first"""

        return Color(self.OTHER)


class Ptype:
    """The class for the type of the piece.

    This class is what determines which type the piece is (e.g. king,
    rook, knight, etc.). It should be used for comparisons between
    two piece's types.

    Attributes:
        TYP {str} -- the short name of the piece -- see "help names"
        NAME {str} -- the full name of the piece
    """


    def __init__(self, typ: Union[str, 'Ptype'], promoted: bool = False):
        """Initialise instance of Ptype.

        Arguments:
            typ {str or Ptype} -- type of piece ('n', 'b', etc.)

        Keyword Arguments:
            promoted {bool} -- if piece is promoted (default: {False})
        """

        typ = str(typ)
        self.TYP: str
        self.NAME: str
        if promoted:
            self.TYP = typ.lower()
            self.NAME = f"+{info.NAMEDICT[self.TYP]}"
        else:
            self.TYP = typ.lower()
            self.NAME = info.NAMEDICT[self.TYP]

    def __str__(self): return self.TYP

    def __repr__(self): return self.NAME

    def __eq__(self, other): return repr(self) == repr(other)

    def __hash__(self): return hash((self.TYP, self.NAME))

    def prom(self) -> 'Ptype':
        """Promote the piece."""
        self.TYP = self.TYP.upper()
        self.NAME = '+'+self.NAME
        return self

    def dem(self) -> 'Ptype':
        """Demote the piece."""
        self.TYP = self.TYP.lower()
        self.NAME = self.NAME.replace('+', '')
        return self


class Moves(collections.abc.Sequence):
    """The class containing the set of moves the piece can do.

    This class contains a dictionary relating directions to the moves
    the piece can make. It also has the ability to test whether or not
    a certain move can be made.

    Attributes:
        NAME {str} -- 1-letter name of piece
        COLOR {Color} -- color of piece
        DMOVES {dict[Direction, str]} -- direction -> move: unpromoted
        PMOVES {dict[Direction, str]} -- dmoves, but for when promoted
        MOVES {list[dict]} -- list [DMOVES, PMOVES]
        ispromoted {bool} -- if the piece is promoted
        CMOVES {dict} -- current set of moves
    """


    def __init__(self, piecenm: Union[str, Ptype], clr: Color, promoted: bool = False):

        """Initialise instance of moves.

        Arguments:
            piecenm {str or Ptype} -- 1-letter name of piece
            clr {Color} -- color of piece

        Keyword Arguments:
            promoted {bool} -- if piece is promoted (default: {False})

        Raises:
            NotPromotableException -- when unpromotable is promoted
        """

        piecenm = str(piecenm)
        pcmvlist = list(info.MOVEDICT[piecenm])
        if clr == Color(1):
            for y, var in enumerate(pcmvlist):
                if var is not None:
                    pcmvlist[y] = var[4:]+var[:4]
        mvlist = pcmvlist[0]
        self.DMOVES: Dict[Direction, str]
        self.NAME = piecenm
        self.COLOR = clr
        self.DMOVES = {Direction(x): mvlist[x] for x in range(8)}
        self.DMOVES[Direction(8)] = '-'
        mvlist = pcmvlist[1]
        self.PMOVES: Optional[Dict[Direction, str]]
        if mvlist is None:
            self.PMOVES = None
        else:
            self.PMOVES = {Direction(x): mvlist[x] for x in range(8)}
            self.PMOVES[Direction(8)] = '-'
        self.MOVES = [self.DMOVES, self.PMOVES]
        self.ispromoted = promoted
        self.CMOVES = self.MOVES[self.ispromoted]
        if self.CMOVES is None:
            raise NotPromotableException

    def __getitem__(self, attr: Direction) -> str:
        if isinstance(attr, Direction):
            return self.CMOVES[attr]
        elif isinstance(attr, int):
            return self.CMOVES[Direction(attr)]
        else:
            raise TypeError

    def __iter__(self) -> Generator: yield from self.CMOVES.values()

    def __len__(self) -> int: return len(self.CMOVES)

    def canmove(self, relloc: Coord) -> bool:
        """Check if piece can move there.

        Arguments:
            relloc {Coord}  -- relative location of move

        Returns:
            bool -- if move is legal
        """

        vec = Direction(relloc)
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
        return False

    def prom(self) -> 'Moves':
        """Promote self.

        Returns:
            Moves -- promoted version of self

        Raises:
            PromotedException -- already promoted
        """

        if self.ispromoted:
            raise PromotedException
        return Moves(self.NAME, self.COLOR, True)

    def dem(self) -> 'Moves':
        """Demote self.

        Returns:
            Moves -- demoted version of self

        Raises:
            DemotedException -- already demoted
        """

        if not self.ispromoted:
            raise DemotedException
        return Moves(self.NAME, self.COLOR, False)
