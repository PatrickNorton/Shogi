from typing import List

from shogi import classes
from shogi.functions import boardtests

__all__ = [
    "test_spaces"
]


def test_spaces(
    current_board: classes.Board,
    piece_location: classes.AbsoluteCoord,
    space_list: List[classes.RelativeCoord],
    checking_spaces: List[classes.AbsoluteCoord] = None
) -> List[classes.AbsoluteCoord]:
    """Test which spaces in a list are valid moves.

    :param current_board: current state of the board
    :param piece_location: location of piece to be moved
    :param space_list: list of coordinates to check
    :param checking_spaces: additional spaces attacking king to check
    :return: list of valid spaces
    """

    if checking_spaces is None:
        checking_spaces = []
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
            king_location, checking_own = boardtests.check_check(
                current_board,
                (piece_location, absolute_location),
                current_board[piece_location].color,
                break_early=True,
                before_move=True
            )
            checking_spaces = [
                x for x in checking_spaces if x != absolute_location
            ]
            if checking_own or king_location == piece_location:
                checking_spaces = []
            for space in checking_spaces:
                try:
                    boardtests.move_check_2(
                        current_board,
                        (space, king_location),
                        ignore_location=piece_location,
                        act_full=absolute_location
                    )
                except classes.IllegalMove:
                    continue
                else:
                    break
            else:
                to_return.append(absolute_location)
    return to_return
