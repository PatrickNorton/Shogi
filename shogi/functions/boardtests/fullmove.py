from typing import List, Tuple

from shogi import classes

from .check import check_check
from .move import move_check_2

__all__ = [
    "check_move",
]


def check_move(
        current_board: classes.Board,
        coordinates: Tuple[classes.AbsoluteCoord, classes.AbsoluteCoord],
        checking_spaces: List[classes.AbsoluteCoord] = None
):
    """A more complete check for if the move is legal.

    :param current_board: current game board
    :param coordinates: move's location: from and to
    :param checking_spaces: spaces checking the current king
    :return: error code
    """
    current, to = coordinates
    if checking_spaces is None:
        checking_spaces = []
    cannot_move = move_check_2(current_board, coordinates)
    if cannot_move:
        return cannot_move
    king_location, checking_own = check_check(
        current_board,
        coordinates,
        current_board.current_player,
        break_early=True,
        before_move=True
    )
    if checking_own:
        return 6
    for space in checking_spaces:
        cannot_move = move_check_2(
            current_board,
            (space, king_location),
            ignore_location=current,
            act_full=to
        )
        if not cannot_move:
            return 6
    return 0
