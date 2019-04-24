from typing import Optional

from .aliases import OptCoordTuple
from .boards import Board
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
    :ivar is_checking: if the move checked the king
    :ivar is_mate: if the move checkmated
    :ivar tuple: (start, end) tuple
    """
    def __init__(
            self,
            current_board: Board,
            move: OptCoordTuple,
            is_drop: bool = False,
            is_capture: bool = False,
            captured_piece: Piece = NoPiece(),
            is_promote: Optional[bool] = None,
            is_checking: bool = False,
            is_mate: bool = False,
    ):
        """Initialise instance of Moves.

        :param current_board: the current board
        :param move: tuple of the start and end of move
        :param is_drop: if the move was a drop
        :param is_capture: if the move was a capture
        :param captured_piece: the captured piece
        :param is_promote: if the move involved promotion
        :param is_checking: if the move caused check
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
        if self.is_promote and not self.piece.is_promoted:
            raise ValueError
        self.is_checking = is_checking
        self.is_mate = is_mate
        if not self.is_checking and self.is_mate:
            raise ValueError
        self.tuple = move

    def __iter__(self): yield from self.tuple
