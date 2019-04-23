from typing import Iterable, Set

from shogi import classes
from .fullmove import check_move

__all__ = [
    "test_spaces",
]


def test_spaces(
        current_board: classes.Board,
        piece_location: classes.AbsoluteCoord,
        to_test: Set[classes.RelativeCoord],
        checking_spaces: Iterable[classes.AbsoluteCoord] = None
) -> classes.CoordSet:
    """Test which spaces in a list are valid moves.

    :param current_board: current state of the board
    :param piece_location: location of piece to be moved
    :param to_test: list of coordinates to check
    :param checking_spaces: additional spaces attacking king to check
    :return: list of valid spaces
    """

    # Set defaults from None to their proper defaults
    if checking_spaces is None:
        checking_spaces = ()
    to_return: classes.CoordSet = set()
    # Test each location in the given list
    for relative_location in to_test:
        # If the new location isn't in the board, it isn't valid,
        # so continue on
        try:
            absolute_location = piece_location + relative_location
        except ValueError:
            continue
        # If the move is valid, add it to the valid-moves list
        if check_move(
            current_board,
            (piece_location, absolute_location),
            checking_spaces,
        ):
            to_return.add(absolute_location)
    return to_return
