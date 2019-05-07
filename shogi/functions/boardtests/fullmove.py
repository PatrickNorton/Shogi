from shogi import classes
from .check import is_check
from .move import is_movable

__all__ = [
    "check_move",
]


def check_move(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        checking_spaces: classes.CoordIter = None
) -> bool:
    """A more complete check for if the move is legal.

    :param current_board: current game board
    :param coordinates: move's location: from and to
    :param checking_spaces: spaces checking the current king
    :return: error code
    """
    current, to = coordinates
    if checking_spaces is None:
        checking_spaces = ()
    # If the piece can't move according to the basic check, it can't
    # according to the more complete one, either
    if not is_movable(current_board, coordinates):
        return False
    # If the piece's move puts the king itself into check, then it's
    # not valid, either
    if is_check(
            current_board,
            coordinates,
            current_board.current_player,
            break_early=True,
            before_move=True
    ):
        return False
    # If any of the already-checking spaces can still attack the king,
    # then the move isn't valid
    king_location = current_board.king_loc(current_board.current_player)
    for space in checking_spaces:
        if is_movable(
            current_board,
            (space, king_location if king_location != current else to),
            ignore_locations=current,
            act_full=to
        ):
            return False
    return True
