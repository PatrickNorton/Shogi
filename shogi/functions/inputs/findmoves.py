from typing import List

from shogi import classes
from shogi.functions import boardtests

__all__ = [
    "test_spaces"
]


def test_spaces(
    current_board: classes.Board,
    piece_location: classes.AbsoluteCoord,
    space_list: List[classes.RelativeCoord]
) -> List[classes.AbsoluteCoord]:
    """Test which spaces in a list are valid moves.

    :param current_board: current state of the board
    :param piece_location: location of piece to be moved
    :param space_list: list of coordinates ot check
    :return: list of valid spaces
    """

    to_return: List[classes.AbsoluteCoord] = []
    for relative_location in space_list:
        try:
            absolute_location = piece_location + relative_location
            boardtests.move_check_2(
                current_board,
                (piece_location, absolute_location)
            )
        except (TypeError, ValueError, classes.IllegalMove):
            continue
        else:
            to_return.append(absolute_location)
    return to_return
