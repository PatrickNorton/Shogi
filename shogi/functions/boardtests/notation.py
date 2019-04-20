from typing import Optional, List

from shogi import classes
from .move import is_movable

__all__ = [
    "to_notation",
    "piece_can_move",
]


def to_notation(
        current_board: classes.Board,
        move: classes.OptCoordTuple,
        is_drop: bool = False,
        is_capture: bool = False,
        is_promote: Optional[bool] = None,
        dropped_piece: Optional[classes.Piece] = None,
        before_move: bool = False,
        is_check: bool = False,
        is_mate: bool = False,
) -> str:
    """Take a move and convert it into shogi notation.

    For information on notation, see notation help.

    :param current_board: current board state
    :param move: tuple of space from, space to
    :param is_drop: if the move was a drop
    :param is_capture: if the move was a capture
    :param is_promote: if the moved piece was promoted
    :param dropped_piece: piece dropped, if applicable
    :param before_move: if this is before the move
    :param is_check: if the move put the king in check
    :param is_mate: if the move put the king in checkmate
    :return: string representing the move
    """
    old_location, new_location = move
    piece = current_board[new_location if not before_move else old_location]
    if is_promote:
        piece_notation = str(piece)[0].lower()
    else:
        piece_notation = str(piece)[0]
    if is_drop:
        if dropped_piece:
            dropped_notation = str(dropped_piece)[0]
            notation = f"{dropped_notation}*{new_location}"
        else:
            if isinstance(piece, classes.NoPiece):
                raise ValueError
            notation = f"{piece_notation}*{new_location}"
    else:
        other_pieces = piece_can_move(current_board, piece, new_location)
        notation = piece_notation
        if other_pieces:
            if all(x.x == old_location.x for x in other_pieces):
                notation += f"{old_location.y_str}"
            elif all(x.y == old_location.y for x in other_pieces):
                notation += f"{old_location.x_str}"
            else:
                notation += f"{old_location}"
        notation += f"{'x' if is_capture else '-'}{new_location}"
        if is_promote is not None:
            notation += '^' if is_promote else '='
    if is_check:
        notation += '#' if is_mate else '+'
    return notation


def piece_can_move(
        current_board: classes.Board,
        piece: classes.Piece,
        to: classes.AbsoluteCoord
) -> List[classes.AbsoluteCoord]:
    """Get list of pieces of the same type which can move
    to a certain location.

    :param current_board: current board state
    :param piece: piece to check for
    :param to: space to test for move to
    :return: list of possible spaces
    """
    if piece in current_board.pieces.items():
        pieces = (
            x for x, y in current_board.pieces.items() if y == piece
        )
        return [x for x in pieces if is_movable(
                    current_board,
                    (x, to),
                    ignore_location=to
                )]
    return []
