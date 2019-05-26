from typing import Iterable

from shogi import classes
from .fullmove import check_move

__all__ = [
    "test_spaces",
]


def test_spaces(
        current_board: classes.Board,
        piece_location: classes.AbsoluteCoord,
        to_test: Iterable[classes.RelativeCoord],
        checking_spaces: classes.CoordIter = (),
) -> classes.CoordGen:
    """Test which spaces in a list are valid moves.

    :param current_board: current state of the board
    :param piece_location: location of piece to be moved
    :param to_test: list of coordinates to check
    :param checking_spaces: additional spaces attacking king to check
    :return: list of valid spaces
    """
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
            yield absolute_location
