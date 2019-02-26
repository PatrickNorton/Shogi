from typing import Optional, List

from shogi import move_check_2
from .aliases import OptCoordTuple
from .boards import Board
from .locations import AbsoluteCoord
from .pieces import Piece, NoPiece

__all__ = [
    "Move",
]


class Move:
    def __init__(
            self,
            current_board: Board,
            move: OptCoordTuple,
            is_drop: bool = False,
            is_capture: bool = False,
            is_promote: Optional[bool] = None,
            dropped_piece: Optional[Piece] = None,
            before_move: bool = False,
            is_check: bool = False,
            is_mate: bool = False,
    ):
        # TODO: Input validation
        self.start = move[0]
        self.end = move[1]
        self.piece = current_board[move[1]]
        self.is_drop = is_drop
        self.is_capture = is_capture
        self.is_promote = is_promote
        self.dropped_piece = dropped_piece
        self.before_move = before_move
        self.is_check = is_check
        self.is_mate = is_mate
        self.tuple = move
        self.string = self.to_string(current_board)

    def __str__(self): return self.string

    def to_string(self, current_board: Board) -> str:
        if self.is_promote:
            piece_notation = str(self.piece)[0].lower()
        else:
            piece_notation = str(self.piece)[0]
        dash = 'x' if self.is_capture else '-'
        if self.is_drop:
            if self.dropped_piece:
                dropped_notation = str(self.dropped_piece)[0]
                notation = f"{dropped_notation}*{self.end}"
            else:
                if isinstance(self.piece, NoPiece):
                    raise ValueError
                notation = f"{piece_notation}*{self.end}"
        else:
            other_pieces = self._piece_can_move(
                current_board, self.piece, self.end)
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

    @staticmethod
    def _piece_can_move(
            current_board: Board,
            piece: Piece,
            to: AbsoluteCoord
    ) -> List[AbsoluteCoord]:
        if piece in current_board.pieces.values():
            pieces = (
                x for x, y in current_board.pieces.values() if y == piece
            )
            valid_spaces = []
            for location in pieces:
                cannot_move = move_check_2(
                    current_board,
                    (location, to),
                    ignore_location=to
                )
                if not cannot_move:
                    valid_spaces.append(location)
            return valid_spaces
        return []
