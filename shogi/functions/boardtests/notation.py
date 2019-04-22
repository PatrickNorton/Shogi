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
        is_checking: bool = False,
        is_mate: bool = False,
) -> str:
    old_location, new_location = move
    piece = current_board[new_location if not before_move else old_location]
    # piece_notation: representing the type of piece
    if is_promote and not before_move:
        # If the moved piece was promoted, demote the piece for the
        # move notation, unless it's before the move, in which case it
        # should already be demoted
        piece_notation = str(piece)[0].lower()
    elif is_drop and dropped_piece:
        # If the piece was dropped, and a dropped piece was specified,
        # the piece notation should be that of the dropped piece
        piece_notation = str(dropped_piece)[0]
    else:
        piece_notation = str(piece)[0]
    # If the piece notation happens to be '-', something has gone
    # badly wrong. Error accordingly
    if piece_notation == '-':
        raise ValueError
    # Other pieces that could move to the new location, were it
    # to be empty
    # TODO: ignore_location & act_full for piece_can_move
    other_pieces = (
            not is_drop and piece_can_move(current_board, piece, new_location)
    )
    # First bit of notation is the notation for the piece
    notation = piece_notation
    # After comes notation differentiating it from all the other
    # pieces that could possibly be moved to the same location
    if other_pieces:
        if all(x.x == old_location.x for x in other_pieces):
            notation += old_location.y_str
        elif all(x.y == old_location.y for x in other_pieces):
            notation += old_location.x_str
        else:
            notation += str(old_location)
    # After that comes the dash, and then the new location
    notation += '*' if is_drop else 'x' if is_capture else '-'
    notation += new_location
    # If the piece was promotable, add char based on promotion
    if is_promote is not None:
        notation += '^' if is_promote else '='
    # If there was check or checkmate, add respective character
    if is_checking:
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
                    current_board, (x, to),
                    ignore_locations=to
                )]
    return []
