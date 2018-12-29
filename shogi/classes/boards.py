from .information import info
from .locations import Coord
from .pieces import piece, nopiece
from .pieceattrs import Color, Ptype
from .exceptions import PromotedException, DemotedException, IllegalMove
from .rows import row

__all__ = [
    "Board"
]


class Board:
    """Class for main board object.

    Attributes:
        PIECES {dict} -- Each Coord and its corresponding piece
        INVPIECES {dict} -- Inverse of PIECES
        CAPTURED {dict} -- List of captured pieces for each color
        PCSBYCLR {dict} -- Same as pieces, but seperated by color
        currplyr {Color} -- Active player
        lastmove {tuple[Coord]} -- Previous move performed
        nextmove {tuple[Coord]} -- Move about to be performed
    """

    def __init__(self, pieces=None):
        """Initialise board.

        Keyword Arguments:
            pieces {dict} -- for custom board setups (default: {None})
        """

        if pieces is None:
            self.PIECES = {Coord(x): piece(*y) for x, y in info.LS.items()}
        else:
            self.PIECES = dict(pieces)
        self.INVPIECES = {v: x for x, v in self.PIECES.items()}
        self.CAPTURED = {Color(x): [] for x in range(2)}
        self.PCSBYCLR = {Color(0): {}, Color(1): {}}
        self.currplyr = Color(0)
        for x in range(2):
            theclr = Color(x)
            for x, y in self.PIECES.items():
                if y.COLOR == theclr:
                    self.PCSBYCLR[theclr][x] = y
        self.lastmove = (None, None)
        self.nextmove = (None, None)

    def __str__(self):
        toreturn = ""
        captostr = [str(x) for x in self.CAPTURED[Color(1)]]
        toreturn += f"Black pieces: {' '.join(captostr)}\n\n"
        toreturn += f"  {'  '.join('987654321')}\n"
        for x, var in enumerate(self):
            toreturn += f"{'abcdefghi'[x]} {' '.join(str(k) for k in var)}\n"
        captostr = [str(x) for x in self.CAPTURED[Color(0)]]
        toreturn += f"White pieces: {' '.join(captostr)}\n"
        return toreturn

    def __iter__(self):
        yield from ([self[x, y] for x in range(9)] for y in range(9))

    def __getitem__(self, index):
        Coords = Coord(index)
        toreturn = self.PIECES.get(Coords, nopiece())
        return toreturn

    def it(self):
        """Yield from all possible board positions."""

        yield from ((x, y) for x in range(9) for y in range(9))

    def occupied(self):
        """Yield from currently occupied spaces."""

        yield from self.PIECES

    def move(self, current, new):
        """Move a piece between locations.

        Arguments:
            current {Coord} -- location of piece
            new {Coord} -- location to move piece to
        """

        if not isinstance(self[new], nopiece):
            self.capture(new)
        self.PIECES[Coord(new)] = self.PIECES.pop(current)
        self.PCSBYCLR[self[new].COLOR][Coord(new)] = self[new]
        del self.PCSBYCLR[self[new].COLOR][Coord(current)]
        self.INVPIECES[self[new]] = new

    def getpiece(self, location):
        """Return a location based on piece type.

        Arguments:
            location {piece} -- piece type to check

        Returns:
            Coord -- location of piece
        """

        return self.INVPIECES[location]

    def capture(self, new):
        """Capture a piece at a location.

        Arguments:
            new {Coord} -- location of to-be-captured piece
        """

        piece = self[new]
        try:
            piece.demote()
        except DemotedException:
            pass
        piece = piece.flipsides()
        self.CAPTURED[self.currplyr].append(piece)
        del self.PIECES[new]
        del self.PCSBYCLR[piece.COLOR.other][Coord(new)]
        if piece in self.PIECES:
            gen = [loc for loc, x in self.PIECES.items() if x == piece]
            self.INVPIECES[piece] = gen[0]
        else:
            del self.INVPIECES[piece]

    def canpromote(self, space):
        """Check if a piece is in a promotion zone.

        Arguments:
            space {Coord} -- location to be checked

        Returns:
            bool -- if piece is promotable
        """

        zonevar = ((0, 1, 2), (8, 7, 6))
        return space.y in zonevar[int(self.currplyr)]

    def autopromote(self, space):
        """Check if piece must be promoted.

        Arguments:
            space {Coord} -- location to be checked

        Returns:
            bool -- if piece must promote
        """

        zonevar = ((0, 1, 2), (8, 7, 6))
        plyrint = int(self.currplyr)
        index = zonevar[plyrint].index(space.y)
        return index < self[space].AUTOPROMOTE

    def promote(self, space):
        """Promote the piece at a location.

        Arguments:
            space {Coord} -- space to promote piece at
        """

        piece = self[space]
        piece = piece.promote()
        self.PIECES[space] = piece
        self.PCSBYCLR[piece.COLOR][space] = piece
        self.INVPIECES[piece] = space

    def putinplay(self, piece, movedto):
        """Move a piece from capture into play.

        Arguments:
            piece {piece} -- the piece to put in play
            movedto {Coord} -- where to put the piece

        Raises:
            IllegalMove -- if capturing on drop
            IllegalMove -- if violating two-pawn rule
        """

        player = self.currplyr
        if not isinstance(self[movedto], nopiece):
            raise IllegalMove(8)
        if piece.PTYPE == Ptype('p'):
            rowtotest = row(movedto, 0)
            for loc in rowtotest.notoriginal():
                if self[loc] == piece('p', player):
                    raise IllegalMove(9)
        self.CAPTURED[player].remove(piece)
        self.PCSBYCLR[piece.COLOR][movedto] = piece
        self.PIECES[movedto] = piece
        self.INVPIECES[piece] = movedto

    @property
    def currpcs(self):
        """dict: Pieces of the current player."""

        return self.PCSBYCLR[self.currplyr]

    @property
    def enemypcs(self):
        """dict: Pieces of opposing player."""

        return self.PCSBYCLR[self.currplyr.other]

    def playerpcs(self, player):
        """Return pieces of specific player

        Arguments:
            player {Color} -- player to return

        Returns:
            dict -- Coords: pieces of player
        """

        return self.PCSBYCLR[player]
