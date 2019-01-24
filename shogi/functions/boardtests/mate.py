from itertools import product
from typing import Set

from shogi import classes
from .move import move_check_2

__all__ = [
    "mate_check"
]


def mate_check(
        current_board: classes.Board,
        king_location: classes.AbsoluteCoord,
        places_attacking: Set[classes.AbsoluteCoord]
) -> bool:
    """Test if king is in checkmate.

    :param current_board:
    :param king_location:
    :param places_attacking:
    :return: if king is in checkmate
    """

    king_moves = (classes.Direction(x) for x in range(8))
    for king_move_tested in king_moves:
        new_location = king_move_tested + king_location
        if tuple(new_location) in current_board.iterate():
            cannot_move = move_check_2(current_board, (king_location, new_location))
            if cannot_move:
                continue
            else:
                return False
    if len(places_attacking) > 1:
        return True
    check_location = places_attacking.pop()
    relative_position = classes.RelativeCoord(king_location - check_location)
    has_pieces = current_board.captured[int(current_board.current_player)]
    not_a_knight = str(current_board[check_location].type) != 'n'
    has_space = not all(x in (-1, 0, 1) for x in relative_position)
    if has_pieces and not_a_knight and has_space:
        return False
    for loc in current_board.enemy_pieces:
        cannot_move = move_check_2(current_board, (loc, check_location))
        if cannot_move:
            continue
        else:
            return False
    move = king_location - check_location
    move_direction = classes.Direction(move)
    for pos, z in product(current_board.enemy_pieces, range(abs(max(move)))):
        new_location = check_location * classes.AbsoluteCoord(move_direction) * z
        cannot_move = move_check_2(current_board, (pos, new_location))
        if cannot_move:
            continue
        else:
            return False
    return True
