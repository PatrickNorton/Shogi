from itertools import product

from shogi import classes
from .move import is_movable

__all__ = [
    "mate_check",
]


def mate_check(
        current_board: classes.Board,
        places_attacking: classes.CoordSet,
        king_color: classes.Color = None,
) -> bool:
    """Test if king is in checkmate.

    :param current_board:
    :param king_color:
    :param places_attacking:
    :return: if king is in checkmate
    """

    if not places_attacking:
        return False
    if king_color is None:
        king_color = next(iter(places_attacking)).color
    king_location = current_board.get_king(king_color)
    for king_move_tested in classes.Direction.valid():
        try:
            new_location = classes.AbsoluteCoord(
                king_move_tested + king_location
            )
        except ValueError:
            continue
        if is_movable(current_board, (king_location, new_location)):
            return False
    if len(places_attacking) > 1:
        return True
    check_location = places_attacking.pop()
    relative_position = classes.RelativeCoord(king_location - check_location)
    has_pieces = current_board.captured[current_board.current_player]
    not_a_knight = not current_board[check_location].has_type('n')
    has_space = not all(x in {-1, 0, 1} for x in relative_position)
    if has_pieces and not_a_knight and has_space:
        return False
    for loc in current_board.enemy_spaces:
        if is_movable(current_board, (loc, check_location)):
            return False
    move = king_location - check_location
    move_direction = classes.Direction(move)
    for pos, z in product(current_board.enemy_spaces, range(max(abs(move)))):
        new_location = check_location * move_direction * z
        if is_movable(current_board, (pos, new_location)):
            return False
    return True
