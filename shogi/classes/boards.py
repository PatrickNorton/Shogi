from .information import info
from .locations import coord
from .pieces import piece, nopiece
from .pieceattrs import color, ptype
from .exceptions import PromotedException, DemotedException, IllegalMove
from .rows import row

__all__ = [
    "board"
]


class board:
    """Class for main board object.

    Attributes:
        PIECES {dict} -- Each coord and its corresponding piece
        INVPIECES {dict} -- Inverse of PIECES
        CAPTURED {dict} -- List of captured pieces for each color
        PCSBYCLR {dict} -- Same as pieces, but seperated by color
        currplyr {color} -- Active player
        lastmove {tuple[coord]} -- Previous move performed
        nextmove {tuple[coord]} -- Move about to be performed
    """

    def __init__(self, pieces=None):
        """Initialise board.

        Keyword Arguments:
            pieces {dict} -- for custom board setups (default: {None})
        """

        if pieces is None:
            self.PIECES = {coord(x): piece(*y) for x, y in info.LS.items()}
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
        toreturn += f"White pieces: {' '.join(captostr)}\n"
        return toreturn

    def __iter__(self):
        yield from ([self[x, y] for x in range(9)] for y in range(9))

    def __getitem__(self, index):
        coords = coord(index)
        toreturn = self.PIECES.get(coords, nopiece())
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
            current {coord} -- location of piece
            new {coord} -- location to move piece to
        """

        if not isinstance(self[new], nopiece):
            self.capture(new)
        self.PIECES[coord(new)] = self.PIECES.pop(current)
        self.PCSBYCLR[self[new].COLOR][coord(new)] = self[new]
        del self.PCSBYCLR[self[new].COLOR][coord(current)]
        self.INVPIECES[self[new]] = new

    def getpiece(self, location):
        """Return a location based on piece type.

        Arguments:
            location {piece} -- piece type to check

        Returns:
            coord -- location of piece
        """

        return self.INVPIECES[location]

    def capture(self, new):
        """Capture a piece at a location.

        Arguments:
            new {coord} -- location of to-be-captured piece
        """

        piece = self[new]
        try:
            piece.demote()
        except DemotedException:
            pass
        piece = piece.flipsides()
        self.CAPTURED[self.currplyr].append(piece)
        del self.PIECES[new]
        del self.PCSBYCLR[piece.COLOR.other][coord(new)]
        if piece in self.PIECES:
            gen = [loc for loc, x in self.PIECES.items() if x == piece]
            self.INVPIECES[piece] = gen[0]
        else:
            del self.INVPIECES[piece]

    def canpromote(self, space):
        """Check if a piece is in a promotion zone.

        Arguments:
            space {coord} -- location to be checked

        Returns:
            bool -- if piece is promotable
        """

        zonevar = ((0, 1, 2), (8, 7, 6))
        return space.y in zonevar[int(self.currplyr)]

    def autopromote(self, space):
        """Check if piece must be promoted.

        Arguments:
            space {coord} -- location to be checked

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
            space {coord} -- space to promote piece at
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
            movedto {coord} -- where to put the piece

        Raises:
            IllegalMove -- if capturing on drop
            IllegalMove -- if violating two-pawn rule
        """

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
            player {color} -- player to return

        Returns:
            dict -- coords: pieces of player
        """

        return self.PCSBYCLR[player]
