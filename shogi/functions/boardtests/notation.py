from typing import Tuple, Optional, List

from shogi import classes

from .move import move_check_2


def to_notation(
        current_board: classes.Board,
        move: Tuple[Optional[classes.AbsoluteCoord], classes.AbsoluteCoord],
        is_drop: bool = False
) -> str:
    old_location, new_location = move
    piece = current_board[new_location]
    piece_notation = str(piece)[0] if not str(piece)[0].isupper() else f"+{piece}"[:1]
    if is_drop:
        if isinstance(piece, classes.NoPiece):
            raise ValueError
        notation = f"{piece_notation}*{new_location}"
        return notation
    else:
        other_pieces = piece_can_move(current_board, piece, new_location)
        if other_pieces:
            if all(x.x == old_location.x for x in other_pieces):
                notation = f"{piece_notation}{old_location.y_str}-{new_location}"
            elif all(x.y == old_location.y for x in other_pieces):
                notation = f"{piece_notation}{old_location.x_str}-{new_location}"
            else:
                notation = f"{piece_notation}{old_location}-{new_location}"
        else:
            notation = f"{piece_notation}-{new_location}"
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
        pieces = [
            x for x, y in current_board.pieces.items() if y == piece
        ]
        valid_spaces = []
        for location in pieces:
            try:
                move_check_2(current_board, (location, to), ignore_location=to)
            except classes.IllegalMove:
                pass
            else:
                valid_spaces.append(location)
        return valid_spaces
