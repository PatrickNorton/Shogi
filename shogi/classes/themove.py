from typing import Optional, List

from shogi.functions.boardtests.move import is_movable
from .aliases import OptCoordTuple
from .boards import Board
from .locations import AbsoluteCoord
from .pieces import Piece, NoPiece

__all__ = [
    "Move",
]


class Move:
    """The class representing a completed move.

    :ivar start: the original position of the piece
    :ivar end: the end location of the piece
    :ivar piece: the piece moved
    :ivar player_color: color of piece moved
    :ivar is_drop: if the move is a drop
    :ivar is_capture: if the move is a capture
    :ivar captured_piece: the captured piece
    :ivar is_promote: if the moved piece was promoted
    :ivar is_check: if the move checked the king
    :ivar is_mate: if the move checkmated
    :ivar tuple: (start, end) tuple
    :ivar string: the move in Shogi move notation
    """
    def __init__(
            self,
            current_board: Board,
            move: OptCoordTuple,
            is_drop: bool = False,
            is_capture: bool = False,
            captured_piece: Piece = NoPiece(),
            is_promote: Optional[bool] = None,
            is_check: bool = False,
            is_mate: bool = False,
    ):
        """Initialise instance of Moves.

        :param current_board: the current board
        :param move: tuple of the start and end of move
        :param is_drop: if the move was a drop
        :param is_capture: if the move was a capture
        :param captured_piece: the captured piece
        :param is_promote: if the move involved promotion
        :param is_check: if the move caused check
        :param is_mate: if the move caused checkmate
        """
        self.start = move[0]
        self.end = move[1]
        self.piece = current_board[move[1]]
        if isinstance(self.piece, NoPiece):
            raise ValueError
        self.player_color = self.piece.color
        self.is_drop = is_drop
        self.is_capture = is_capture
        self.captured_piece = captured_piece
        if self.is_capture and isinstance(self.captured_piece, NoPiece):
            raise ValueError
        self.is_promote = is_promote
        if self.is_promote and not self.piece.prom:
            raise ValueError
        self.is_check = is_check
        self.is_mate = is_mate
        if not self.is_check and self.is_mate:
            raise ValueError
        self.tuple = move
        self.string = self.to_string(current_board)

    def __str__(self): return self.string

    def __iter__(self): yield from self.tuple

    def to_string(self, current_board: Board) -> str:
        """Create notation string out of the move.

        :param current_board: current board state
        :return: notation string
        """
        if self.is_promote:
            piece_notation = str(self.piece)[0].lower()
        else:
            piece_notation = str(self.piece)[0]
        dash = 'x' if self.is_capture else '-'
        if self.is_drop:
            if isinstance(self.piece, NoPiece):
                raise ValueError
            notation = f"{piece_notation}*{self.end}"
        else:
            other_pieces = _piece_can_move(current_board, self.piece, self.end)
            notation = piece_notation
            if other_pieces:
                if all(x.x == self.start.x for x in other_pieces):
                    notation += self.start.y_str
                elif all(x.y == self.start.y for x in other_pieces):
                    notation += self.start.x_str
                else:
                    notation += str(self.start)
            notation += f"{dash}{self.end}"
            if self.is_promote is not None:
                notation += '^' if self.is_promote else '='
        if self.is_check:
            notation += '#' if self.is_mate else '+'
        return notation


def _piece_can_move(
        current_board: Board,
        piece: Piece,
        to: AbsoluteCoord
) -> List[AbsoluteCoord]:
    """Check if any pieces can move to a location.

    This is a mirror of the function in shogi.functions.
    It exists in order to prevent circular imports.
    Please change with caution.

    :param current_board: current board state
    :param piece: piece to check for move
    :param to: space piece is moved to
    :return: list of possible spaces that can move there
    """
    if piece in current_board.pieces.values():
        pieces = (
            x for x, y in current_board.pieces.items() if y == piece
        )
        valid_spaces = []
        for location in pieces:
            if is_movable(current_board, (location, to), ignore_location=to):
                valid_spaces.append(location)
        return valid_spaces
    return []
