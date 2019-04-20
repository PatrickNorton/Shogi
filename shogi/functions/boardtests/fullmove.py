from typing import Iterable

from shogi import classes
from .check import check_check
from .move import is_movable

__all__ = [
    "check_move",
]


def check_move(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        checking_spaces: Iterable[classes.AbsoluteCoord] = None
):
    """A more complete check for if the move is legal.

    :param current_board: current game board
    :param coordinates: move's location: from and to
    :param checking_spaces: spaces checking the current king
    :return: error code
    """
    current, to = coordinates
    if checking_spaces is None:
        checking_spaces = ()
    can_move = is_movable(current_board, coordinates)
    if not can_move:
        return False
    king_location, checking_own = check_check(
        current_board,
        coordinates,
        current_board.current_player,
        break_early=True,
        before_move=True
    )
    if checking_own:
        return False
    for space in checking_spaces:
        can_move = is_movable(
            current_board,
            (space, king_location),
            ignore_locations=current,
            act_full=to
        )
        if can_move:
            return False
    return True
