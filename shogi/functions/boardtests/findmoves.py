from typing import List, Iterable

from shogi import classes
from shogi.functions import boardtests

__all__ = [
    "test_spaces",
]


def test_spaces(
        current_board: classes.Board,
        piece_location: classes.AbsoluteCoord,
        space_list: List[classes.RelativeCoord],
        checking_spaces: Iterable[classes.AbsoluteCoord] = None
) -> classes.CoordSet:
    """Test which spaces in a list are valid moves.

    :param current_board: current state of the board
    :param piece_location: location of piece to be moved
    :param space_list: list of coordinates to check
    :param checking_spaces: additional spaces attacking king to check
    :return: list of valid spaces
    """

    if checking_spaces is None:
        checking_spaces = ()
    to_return: classes.CoordSet = set()
    for relative_location in space_list:
        try:
            absolute_location = classes.AbsoluteCoord(
                piece_location + relative_location
            )
        except ValueError:
            continue
        if isinstance(absolute_location, classes.RelativeCoord):
            continue
        can_move = boardtests.is_movable(
            current_board,
            (piece_location, absolute_location)
        )
        if can_move:
            king_color = current_board[piece_location].color
            checking_own = boardtests.is_check(
                current_board,
                (piece_location, absolute_location),
                king_color,
                break_early=True,
                before_move=True
            )
            checking_spaces = (
                x for x in checking_spaces if x != absolute_location
            )
            king_location = current_board.get_king(king_color)
            if checking_own or king_location == piece_location:
                checking_spaces = ()
            for space in checking_spaces:
                if boardtests.is_movable(
                        current_board,
                        (space, king_location),
                        ignore_locations=piece_location,
                        act_full=absolute_location):
                    break
            else:
                to_return.add(absolute_location)
    return to_return