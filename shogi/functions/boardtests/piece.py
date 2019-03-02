from shogi import classes

from .goodinput import input_piece

__all__ = [
    "piece_check",
]


def piece_check(
        current_board: classes.Board,
        piece_string: str
) -> classes.AbsoluteCoord:
    """Check if inputted piece is valid.

    :param current_board: current board state
    :param piece_string: inputted string of location
    :raises classes.IllegalMove: invalid entry of piece
    :raises classes.IllegalMove: entry of location without right piece
    :return: location inputted
    """

    is_valid: bool = input_piece(piece_string)
    if not is_valid:
        raise ValueError
    piece_location = classes.AbsoluteCoord(piece_string)
    if current_board[piece_location].color != current_board.current_player:
        raise ValueError
    return piece_location
