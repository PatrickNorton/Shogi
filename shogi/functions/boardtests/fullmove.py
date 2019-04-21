from typing import Iterable

from shogi import classes
from .check import is_check
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
    if not is_movable(current_board, coordinates):
        return False
    if is_check(
            current_board,
            coordinates,
            current_board.current_player,
            break_early=True,
            before_move=True
    ):
        return False
    for space in checking_spaces:
        king_location = current_board.get_king(current_board.current_player)
        if is_movable(
            current_board,
            (space, king_location),
            ignore_locations=current,
            act_full=to
        ):
            return False
    return True
