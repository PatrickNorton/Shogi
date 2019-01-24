import collections

from typing import Dict, List, Generator, Sequence, Optional

from .information import info
from .locations import AbsoluteCoord, NullCoord
from .pieces import Piece, NoPiece
from .pieceattrs import Color
from .exceptions import DemotedException
from .rows import Row

__all__ = [
    "Board"
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
    :ivar inverse_pieces: Inverse of pieces
    :ivar captured: List of captured pieces for each color
    :ivar by_color: Same as pieces, but separated by color
    :ivar current_player: Active player
    :ivar last_move: Previous move performed
    :ivar next_move: Move about to be performed
    """

    def __init__(self, pieces: Optional[dict] = None):
        """Initialise board.

        :param pieces: for custom board setups
        """

        self.pieces: Dict[AbsoluteCoord, Piece]
        if pieces is None:
            self.pieces = {AbsoluteCoord(x): Piece(*y) for x, y in info.board_info.items()}
        else:
            self.pieces = {AbsoluteCoord(x): Piece(*y) for x, y in pieces.items()}
        self.inverse_pieces = {v: x for x, v in self.pieces.items()}
        self.captured: Dict[Color, List[Piece]]
        self.captured = {Color(x): [] for x in range(2)}
        self.by_color: Dict[Color, Dict[AbsoluteCoord, Piece]]
        self.by_color = {Color(0): {}, Color(1): {}}
        self.current_player = Color(0)
        for x in range(2):
            x_color = Color(x)
            for loc, pc in self.pieces.items():
                if pc.is_color(x_color):
                    self.by_color[x_color][loc] = pc
        self.last_move = (NullCoord(), NullCoord())
        self.next_move = (NullCoord(), NullCoord())

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

    @staticmethod
    def iterate() -> Generator:
        """Yield from all possible board positions."""

        yield from ((x, y) for x in range(9) for y in range(9))

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
        self.by_color[self[new].color][AbsoluteCoord(new)] = self[new]
        del self.by_color[self[new].color][AbsoluteCoord(current)]
        self.inverse_pieces[self[new]] = new

    def get_piece(self, piece_name: Piece) -> AbsoluteCoord:
        """Return a location based on piece type.

        :param piece_name: piece type to check
        :return: location of piece
        """

        return self.inverse_pieces[piece_name]

    def capture(self, new: AbsoluteCoord):
        """Capture a piece at a location.

        :param new: location of to-be-captured piece
        """

        piece = self[new]
        try:
            piece.demote()
        except DemotedException:
            pass
        new_piece = piece.flip_sides()
        self.captured[self.current_player].append(new_piece)
        del self.pieces[new]
        del self.by_color[piece.color][AbsoluteCoord(new)]
        if piece in self.pieces.values():
            gen = [loc for loc, x in self.pieces.items() if x == piece]
            self.inverse_pieces[piece] = gen[0]
        else:
            del self.inverse_pieces[piece]

    def can_promote(self, space: AbsoluteCoord) -> bool:
        """Check if a piece is in a promotion zone.

        :param space: location to be checked
        :return: if piece is promotable
        """

        promotion_zones = ((0, 1, 2), (8, 7, 6))
        return space.y in promotion_zones[int(self.current_player)]

    def auto_promote(self, space: AbsoluteCoord) -> bool:
        """Check if piece must be promoted.

        :param space: location to be checked
        :return: if piece must promote
        """

        promotion_zones = ((0, 1, 2), (8, 7, 6))
        player_int = int(self.current_player)
        index = promotion_zones[player_int].index(space.y)
        return index < self[space].auto_promote

    def promote(self, space: AbsoluteCoord):
        """Promote the piece at a location.

        :param space: space to promote piece at
        :return:
        """

        piece = self[space]
        piece = piece.promote()
        self.pieces[space] = piece
        self.by_color[piece.color][space] = piece
        self.inverse_pieces[piece] = space

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
        self.by_color[piece.color][moved_to] = piece
        self.pieces[moved_to] = piece
        self.inverse_pieces[piece] = moved_to

    @property
    def current_pieces(self) -> Dict[AbsoluteCoord, Piece]:
        """dict: Pieces of the current player."""

        return self.by_color[self.current_player]

    @property
    def enemy_pieces(self) -> Dict[AbsoluteCoord, Piece]:
        """dict: Pieces of opposing player."""

        return self.by_color[self.current_player.other]

    def player_pieces(self, player: Color) -> Dict[AbsoluteCoord, Piece]:
        """Return pieces of specific player

        :param player: player to return
        :return: pieces of player
        """

        return self.by_color[player]
