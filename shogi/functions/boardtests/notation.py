from typing import Tuple, Optional, List

from shogi import classes

from .move import move_check_2


def to_notation(
        current_board: classes.Board,
        move: Tuple[Optional[classes.AbsoluteCoord], classes.AbsoluteCoord],
        is_drop: bool = False,
        is_capture: bool = False,
        is_promote: Optional[bool] = None
) -> str:
    old_location, new_location = move
    piece = current_board[new_location]
    if is_promote:
        piece_notation = str(piece)[0].lower()
    elif not str(piece)[0].isupper():
        piece_notation = str(piece)[0]
    else:
        piece_notation = f"+{str(piece)}"
    dash = 'x' if is_capture else '-'
    if is_drop:
        if isinstance(piece, classes.NoPiece):
            raise ValueError
        notation = f"{piece_notation}*{new_location}"
    else:
        other_pieces = piece_can_move(current_board, piece, new_location)
        notation = piece_notation
        if other_pieces:
            if all(x.x == old_location.x for x in other_pieces):
                notation += f"{old_location.y_str}{dash}{new_location}"
            elif all(x.y == old_location.y for x in other_pieces):
                notation += f"{old_location.x_str}{dash}{new_location}"
            else:
                notation += f"{old_location}{dash}{new_location}"
        else:
            notation += f"{dash}{new_location}"
        if is_promote is not None:
            notation += '+' if is_promote else '='
    return notation


def piece_can_move(
        current_board: classes.Board,
        piece: classes.Piece,
        to: classes.AbsoluteCoord
) -> List[classes.AbsoluteCoord]:
    try:
        current_board.inverse_pieces[piece]
    except KeyError:
        return []
    else:
        pieces = (
            x for x, y in current_board.pieces.items() if y == piece
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
