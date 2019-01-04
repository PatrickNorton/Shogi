from itertools import product
from shogi import classes
from .move import move_check_2
from typing import List

__all__ = [
    "mate_check"
]


def mate_check(
    current_board: classes.Board,
    king_location: classes.Coord,
    places_attacking: List[classes.Coord]
) -> bool:
    """Test if king is in checkmate.

    Arguments:
        current_board {Board} -- current board position
        king_location {Coord} -- location of king
        places_attacking {list[Coord]} -- list of pieces checking king

    Returns:
        bool -- if king is in checkmate
    """

    king_moves = (classes.Direction(x) for x in range(8))
    for king_move_tested in king_moves:
        new_location = king_move_tested + king_location
        if tuple(new_location) in current_board.it():
            try:
                move_check_2(current_board, (king_location, new_location))
            except classes.IllegalMove:
                continue
            else:
                return False
    if len(places_attacking) > 1:
        return True
    check_location = places_attacking[0]
    relative_position = king_location - check_location
    has_pieces = current_board.CAPTURED[int(current_board.currplyr)]
    not_a_knight = str(current_board[check_location].PTYPE) != 'n'
    has_space = not all(x in (-1, 0, 1) for x in relative_position)
    if has_pieces and not_a_knight and has_space:
        return False
    for loc in current_board.enemypcs:
        try:
            move_check_2(current_board, (loc, check_location))
        except classes.IllegalMove:
            continue
        return False
    move = king_location - check_location
    move_direction = classes.Direction(move)
    for pos, z in product(current_board.enemypcs, range(abs(max(move)))):
        new_location = check_location*classes.Coord(move_direction)*z
        try:
            move_check_2(current_board, (pos, new_location))
        except classes.IllegalMove:
            continue
        return False
    return True
