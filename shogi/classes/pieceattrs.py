from .locations import Direction
from .information import info

__all__ = [
    "Color",
    "Ptype",
    "Moves"
]


class Color:
    """The class for piece/player colors.

    This class covers both the color for a piece and the player colors.
    Use accordingly.

    Attributes:
        INT {int} -- the integer (white=0, black=1) of the turn
        NAME {str} -- the character (w, b) of the color
        OTHER {str} -- the character of the other color
        FULLNM {str} -- the full name (White, Black) of the color
    """

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

    def flip(self):
        """DEPRECATED: Get the opposite color.

        Returns:
            Color -- the other color
        """

        return Color(int(not self.INT))

    @property
    def other(self):
        """Color: Opposite color from first"""

        return Color(self.OTHER)


class Ptype:
    """The class for the type of the piece.

    This class contains the different attributes of the piece's type.

    Attributes:
        TYP {str} -- the short name of the piece -- see "help names"
        NAME {str} -- the full name of the piece
    """

    def __init__(self, typ):
        typ = str(typ)
        self.TYP = typ.lower()
        self.NAME = info.NAMEDICT[self.TYP]

    def __str__(self): return self.TYP

    def __repr__(self): return self.NAME

    def __eq__(self, other): return repr(self) == repr(other)

    def __hash__(self): return hash((self.TYP, self.NAME))

    def prom(self):
        """Promote the piece."""
        self.TYP = self.TYP.upper()
        self.NAME = '+'+self.NAME
        return self

    def dem(self):
        """Demote the piece."""
        self.TYP = self.TYP.lower()
        self.NAME = self.NAME.replace('+', '')
        return self


class Moves:
    """The class containing the set of moves the piece can do.

    Attributes:
        DMOVES {dict} -- dict from direction -> move when unpromoted
        PMOVES {dict} -- dmoves, but for when promoted
        MOVES {list[dict]} -- list [DMOVES, PMOVES]
        ispromoted {bool} -- if the piece is promoted
        CMOVES {dict} -- current set of moves
    """

    def __init__(self, piecenm, clr):
        """Initialise instance of moves.

        Arguments:
            piecenm {str} -- 1-letter name of piece
            clr {Color} -- color of piece
        """

        piecenm = str(piecenm)
        pcmvlist = list(info.MOVEDICT[piecenm])
        if clr == Color(1):
            for y, var in enumerate(pcmvlist):
                if var is not None:
                    pcmvlist[y] = var[4:]+var[:4]
        mvlist = pcmvlist[0]
        self.DMOVES = {Direction(x): mvlist[x] for x in range(8)}
        self.DMOVES[Direction(8)] = '-'
        mvlist = pcmvlist[1]
        if mvlist is None:
            self.PMOVES = None
        else:
            self.PMOVES = {Direction(x): mvlist[x] for x in range(8)}
            self.PMOVES[Direction(8)] = '-'
        self.MOVES = [self.DMOVES, self.PMOVES]
        self.ispromoted = False
        self.CMOVES = self.MOVES[self.ispromoted]

    def __getitem__(self, attr): return self.CMOVES[attr]

    def __iter__(self): yield from self.CMOVES

    def canmove(self, relloc):  # Takes Coord object
        """Check if piece can move there.

        Arguments:
            relloc {Coord  -- relative location of move

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

    def prom(self):
        """Promote self.

        Returns:
            Moves -- promoted version of self
        """

        self.ispromoted = True
        self.CMOVES = self.MOVES[self.ispromoted]
        return self

    def dem(self):
        """Demote self.

        Returns:
            Moves -- demoted version of self
        """

        self.ispromoted = False
        self.CMOVES = self.MOVES[self.ispromoted]
        return self
