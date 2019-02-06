import collections
from typing import Dict, Generator, List, Optional, Sequence

from .aliases import CoordTuple, PieceDict
from .exceptions import DemotedException
from .information import info
from .locations import AbsoluteCoord, NullCoord
from .pieceattrs import Color, ColorLike
from .pieces import Piece, NoPiece
from .rows import Row

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
    :ivar last_move: Previous move performed
    :ivar next_move: Move about to be performed
    """

    def __init__(self, pieces: Optional[dict] = None):
        """Initialise board.

        :param pieces: for custom board setups
        """

        if pieces is None:
            self.pieces: PieceDict = {
                AbsoluteCoord(x): Piece(*y) for x, y in info.board_info.items()
            }
        else:
            self.pieces: PieceDict = {
                AbsoluteCoord(x): Piece(*y) for x, y in pieces.items()
            }
        self.captured: Dict[Color, List[Piece]] = {
            x: [] for x in Color.valid()
        }
        self.current_player: Color = Color(0)
        self.last_move: CoordTuple = (NullCoord(), NullCoord())
        self.next_move: CoordTuple = (NullCoord(), NullCoord())
        self.kings: Dict[Color, AbsoluteCoord] = {}
        for x, y in self.pieces.items():
            if y.has_type('k'):
                self.kings[y.color] = x

    def __str__(self):
        to_return = ""
        captured_string = [str(x) for x in self.captured[Color(1)]]
        to_return += f"Black pieces: {' '.join(captured_string)}\n\n"
        to_return += f"  {'  '.join('987654321')}\n"
        for x, var in enumerate(self):
            to_return += f"{'abcdefghi'[x]} {' '.join(str(k) for k in var)}\n"
        captured_string = [str(x) for x in self.captured[Color(0)]]
        to_return += f"White pieces: {' '.join(captured_string)}\n"
        return to_return

    def __iter__(self) -> Generator:
        yield from ([self[x, y] for x in range(9)] for y in range(9))

    def __getitem__(self, index: Sequence) -> Piece:
        coordinates = AbsoluteCoord(index)
        to_return = self.pieces.get(coordinates, NoPiece())
        return to_return

    def __len__(self) -> int: return len(tuple(self))

    def __repr__(self): return f"Board(pieces={self.pieces})"

    @staticmethod
    def iterate() -> Generator:
        """Yield from all possible board positions."""

        yield from ((x, y) for y in range(9) for x in range(9))

    @property
    def occupied(self) -> Generator:
        """Yield from currently occupied spaces."""

        yield from self.pieces

    def move(self, current: AbsoluteCoord, new: AbsoluteCoord):
        """Move a piece between locations.

        :param current: location of piece
        :param new: location to move piece to
        """

        if not isinstance(self[new], NoPiece):
            self.capture(new)
        self.pieces[AbsoluteCoord(new)] = self.pieces.pop(current)
        if self.pieces[new].has_type('k'):
            self.kings[self.pieces[new].color] = new

    def get_king(self, king_color: ColorLike) -> AbsoluteCoord:
        """Return a location based on piece type.

        :param king_color: piece type to check
        :return: location of piece
        """

        for x, y in self.pieces.items():
            if y.is_piece('k', king_color):
                return x

    def capture(self, new: AbsoluteCoord):
        """Capture a piece at a location.

        :param new: location of to-be-captured piece
        """

        piece = self[new]
        if piece.has_type('k'):
            raise ValueError("Kings may not be captured. You win.")
        try:
            piece.demote()
        except DemotedException:
            pass
        new_piece = piece.flip_sides()
        self.captured[self.current_player].append(new_piece)
        del self.pieces[new]

    def can_promote(self, space: AbsoluteCoord) -> bool:
        """Check if a piece is in a promotion zone.

        :param space: location to be checked
        :return: if piece is promotable
        """

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

        if piece == NoPiece():
            piece = self[space]
        promotion_zones = ((0, 1, 2), (8, 7, 6))
        player_int = int(self.current_player)
        try:
            index = promotion_zones[player_int].index(space.y)
        except ValueError:
            return False
        else:
            return index < piece.auto_promote

    def promote(self, space: AbsoluteCoord):
        """Promote the piece at a location.

        :param space: space to promote piece at
        :return:
        """

        piece = self[space]
        piece = piece.promote()
        self.pieces[space] = piece

    def put_in_play(self, piece: Piece, moved_to: AbsoluteCoord):
        """Move a piece from capture into play.

        :param piece: the piece to put in play
        :param moved_to: where to put the piece
        :raises IllegalMove: if capturing on drop
        :raises IllegalMove: if capturing 2-pawn rule
        """

        player = self.current_player
        if not isinstance(self[moved_to], NoPiece):
            return 8
        if piece.has_type('p'):
            row_to_test = Row(moved_to, 0)
            for loc in row_to_test.not_original:
                if self[loc].is_piece('p', player):
                    return 9
        self.captured[player].remove(piece)
        self.pieces[moved_to] = piece

    def flip_turn(self):
        """Flip the turn from one player to the other."""
        self.current_player = self.other_player

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
