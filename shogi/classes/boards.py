import collections
from itertools import product
from typing import Dict, Generator, List, Optional, Sequence

from .aliases import PieceDict
from .exceptions import DemotedException
from .information import info
from .locations import AbsoluteCoord
from .pieceattrs import Color, ColorLike
from .pieces import Piece, NoPiece

__all__ = [
    "Board",
]


class Board(collections.abc.Sequence):
    """Class for main board object.


    This is the object representing the main game board, and has,
    additionally, several functions related to play of game. An
    instance of this should be passed any functions with an input
    parameter of "current_board", and should represent the current
    state of the game, up to, but not including, the current move,
    unless the current move has been checked. The move to be checked
    should be stored in the "next_move" attribute, while the previous
    move made should be stored in the "last_move" attribute.

    :ivar pieces: Each coordinate and corresponding piece
    :ivar captured: List of captured pieces for each color
    :ivar current_player: Active player
    """

    def __init__(self, pieces: Optional[dict] = None):
        """Initialise board.

        :param pieces: for custom board setups
        """

        # Use the standard setup if nothing is given
        if pieces is None:
            pieces = info.board_info
        # Dict mapping locations to occupants
        self.pieces: PieceDict = {
            AbsoluteCoord(x): Piece(*y) for x, y in pieces.items()
        }
        # Captured pieces for each color
        self.captured: Dict[Color, List[Piece]] = {
            x: [] for x in Color.valid()
        }
        # Color of whomever's turn it is
        self.current_player: Color = Color(0)
        # Dict mapping kings to their locations
        self.kings: Dict[Color, AbsoluteCoord] = {}
        # Number of spaces wide the board is
        self.x_size: int = 9
        # Ditto, but for height
        self.y_size: int = 9
        # Setup self.kings
        for x, y in self.pieces.items():
            if y.is_rank('k'):
                self.kings[y.color] = x

    def __str__(self):
        to_return = ""
        # Black's captured pieces
        captured_string = (str(x) for x in self.captured[Color(1)])
        to_return += f"Black pieces: {' '.join(captured_string)}\n\n"
        # Column numbers
        to_return += f"  {'  '.join('123456789')}\n"
        # Each row of the board
        for x, var in enumerate(self):
            to_return += f"{'abcdefghi'[::-1][x]} "
            to_return += f"{' '.join(str(k) for k in var)}\n"
        # White's captured pieces
        captured_string = (str(x) for x in self.captured[Color(0)])
        to_return += f"White pieces: {' '.join(captured_string)}\n"
        return to_return

    def __iter__(self) -> Generator:
        # y and x reversed so that board doesn't come out sideways
        # Thanks, itertools
        for y, x in product(range(self.y_size), range(self.x_size)):
            yield self[x, y]

    def __getitem__(self, index: Sequence) -> Piece:
        coordinates = AbsoluteCoord(index)
        return self.pieces.get(coordinates, NoPiece())

    def __len__(self) -> int: return len(tuple(self))

    def __repr__(self): return f"Board(pieces={self.pieces})"

    def iterate(self) -> Generator:
        """Yield from all possible board positions."""

        for y, x in product(range(self.y_size), range(self.x_size)):
            yield AbsoluteCoord((x, y))

    @property
    def occupied(self) -> Generator:
        """Yield from currently occupied spaces."""

        yield from self.pieces

    def move(self, current: AbsoluteCoord, new: AbsoluteCoord):
        """PieceMove a piece between locations.

        :param current: location of piece
        :param new: location to move piece to
        """

        # If there's a piece in the way, capture it
        if not isinstance(self[new], NoPiece):
            self.capture(new)
        # Get the piece to be moved
        self.pieces[AbsoluteCoord(new)] = self.pieces.pop(current)
        # If the piece is a king, update self.kings accordingly
        if self.pieces[new].is_rank('k'):
            self.kings[self.pieces[new].color] = new

    def get_king(self, king_color: ColorLike) -> AbsoluteCoord:
        """Return the location of a color's king.

        :param king_color: color of king to check
        :return: location of piece
        """

        # Search through the pieces until the king is found
        for x, y in self.pieces.items():
            if y.is_piece('k', king_color):
                return x

    def capture(self, new: AbsoluteCoord):
        """Capture a piece at a location.

        :param new: location of to-be-captured piece
        """

        piece = self[new]
        if piece.is_rank('k'):
            raise ValueError("Kings may not be captured. You win.")
        # If the captured piece is promoted, demote it
        try:
            piece = piece.demote()
        except DemotedException:
            pass
        # Flip the side of the piece, so it belongs to the captors
        new_piece = piece.flip_sides()
        # Add it to the captured pieces
        self.captured[self.current_player].append(new_piece)
        # Remove the piece from where it was
        del self.pieces[new]

    def can_promote(self, space: AbsoluteCoord) -> bool:
        """Check if a piece is in a promotion zone.

        :param space: location to be checked
        :return: if piece is promotable
        """

        # Return whether or not the piece is far enough along the
        # board to promote
        promotion_zones = ((0, 1, 2), (8, 7, 6))
        return space.y in promotion_zones[int(self.current_player)]

    def auto_promote(
            self,
            space: AbsoluteCoord,
            piece: Piece = NoPiece()
    ) -> bool:
        """Check if piece must be promoted.

        :param space: location to be checked
        :param piece: piece to check for auto-promotion
        :return: if piece must promote
        """

        # If the piece is not supplied, get it from the space
        if isinstance(piece, NoPiece):
            piece = self[space]
        # See if the piece can promote, and get how far it is from the
        # edge of the board
        promotion_zones = ((0, 1, 2), (8, 7, 6))
        player_int = int(self.current_player)
        try:
            index = promotion_zones[player_int].index(space.y)
        # If the piece can't promote (it is not in the promotion_zones
        # list, then it can;t be promoted, and so will not
        # automatically promote
        except ValueError:
            return False
        # If the piece is able to promote, check how far it is from
        # the edge, and compare that to where it is forced to promote
        else:
            return index < piece.auto_promote

    def promote(self, space: AbsoluteCoord):
        """Promote the piece at a location.

        :param space: space to promote piece at
        """

        piece = self[space]
        piece = piece.promote()
        self.pieces[space] = piece

    def demote(self, space: AbsoluteCoord):
        """Demote the piece at a location.

        :param space: space to demote at
        """
        piece = self[space]
        piece = piece.demote()
        self.pieces[space] = piece

    def put_in_play(
            self,
            piece: Piece,
            moved_to: AbsoluteCoord,
            player: Color = None,
            flip_sides: bool = False
    ):
        """Moves a piece from capture into play.

        :param piece: the piece to put in play
        :param moved_to: where to put the piece
        :param player: color of piece to put in play
        :param flip_sides: if the piece should flip sides
        """

        # Figure out the color of the piece to put in play
        if player is None:
            player = self.current_player
        # If there's already a piece at the moved-to spot, error
        if not isinstance(self[moved_to], NoPiece):
            raise ValueError
        # Move the piece to where it needs to go
        self.captured[player].remove(piece)
        if flip_sides:
            piece = piece.flip_sides()
        self.pieces[moved_to] = piece

    def un_drop(self, location: AbsoluteCoord):
        """Un-drop piece.

        This takes a piece and put it back into the captured slots.
        This should not be used in an actual game, as it is illegal.
        It exists solely for undoing of moves.

        :param location: location of piece to un-drop
        """
        un_dropped = self.pieces.pop(location)
        # Demote the piece, if it is not already demoted
        try:
            un_dropped = un_dropped.demote()
        except DemotedException:
            pass
        self.captured[un_dropped.color].append(un_dropped)

    def flip_turn(self):
        """Flip the turn from one player to the other."""
        self.current_player = self.other_player

    def row(self, row_num: int) -> Generator:
        """The pieces at each space in a row of the board."""
        for y in range(self.y_size):
            yield self[AbsoluteCoord((row_num, y))]

    def filled_row(self, row_num: int) -> Generator:
        """The occupied pieces from each space in a row."""
        for y in range(self.y_size):
            space = AbsoluteCoord((row_num, y))
            if self[space]:
                yield self[space]

    def column(self, col_num: int) -> Generator:
        """The pieces at each space in a column of the board."""
        for x in range(self.x_size):
            yield self[AbsoluteCoord((x, col_num))]

    def filled_column(self, col_num: int) -> Generator:
        """The occupied pieces from each space in a column."""
        for x in range(self.x_size):
            space = AbsoluteCoord((x, col_num))
            if self[space]:
                yield self[space]

    @property
    def current_pieces(self) -> Generator:
        """dict: Pieces of the current player."""

        for x, y in self.pieces.items():
            if y.is_color(self.other_player):
                yield (x, y)

    @property
    def enemy_pieces(self) -> Generator:
        """dict: Pieces of opposing player."""

        for x, y in self.pieces.items():
            if y.is_color(self.other_player):
                yield (x, y)

    @property
    def enemy_spaces(self) -> Generator:
        for x, y in self.pieces.items():
            if y.is_color(self.other_player):
                yield x

    @property
    def other_player(self) -> Color:
        return Color(self.current_player.other_color)

    def player_pieces(self, player: Color) -> Generator:
        """Return generator yielding loc, piece pairs for player.

        :param player: player to return
        :return: pieces of player
        """

        for x, y in self.pieces.items():
            if y.is_color(player):
                yield (x, y)
