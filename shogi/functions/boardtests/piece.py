from shogi import classes
from .goodinput import input_piece

__all__ = [
    "piece_check"
]


def piece_check(
    current_board: classes.Board,
    piece_string: str
):
    """Check if inputted piece is valid.

    Arguments:
        current_board {Board} -- current board state
        piece_string {str} -- inputted string of location

    Raises:
        classes.IllegalMove -- invalid entry of piece
        classes.IllegalMove -- entry of location without their piece

    Returns:
        Coord -- location inputted
    """

    is_valid: bool = input_piece(piece_string)
    if not is_valid:
        raise classes.IllegalMove(11)
    piece_location = classes.Coord(piece_string)
    if current_board[piece_location].COLOR != current_board.currplyr:
        raise classes.IllegalMove(5)
    return piece_location
