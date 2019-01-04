from shogi import classes
from .move import move_check_2
from typing import List, Tuple

__all__ = [
    "check_check",
    "check_check_2"
]


def check_check(
    current_board: classes.Board,
    coordinates: Tuple[classes.Coord, classes.Coord],
    king_color: classes.Color,
    break_early: bool = False
) -> Tuple[bool, classes.Coord, List[classes.Coord]]:
    """Find if king is in check.

    Arguments:
        current_board {Board} -- current game board
        coordinates {tuple[Coord]} -- last move (from, to)
        king_color {Color} -- king_color of king to test

    Keyword Arguments:
        break_early {bool} -- break after first or second check
            (default: {False})

    Returns:
        bool -- if king is in check
        Coord -- location of king
        list[Coord] -- list of coordinates attacking king
    """

    old_location, new_location = coordinates
    places_attacking: List[classes.Coord] = []
    king_tested: classes.Piece = classes.Piece('k', king_color)
    king_location: classes.Coord = current_board.getpiece(king_tested)
    try:
        move_check_2(current_board, (new_location, king_location))
    except classes.IllegalMove:
        check, places_attacking = check_check_2(
            current_board,
            (old_location, king_location),
            places_attacking,
            break_early)
    else:
        if break_early:
            places_attacking.append(new_location)
            return True, king_location, places_attacking
        else:
            places_attacking.append(new_location)
            check, places_attacking = check_check_2(
                current_board,
                (old_location, king_location),
                places_attacking)
            return True, king_location, places_attacking
    return check, king_location, places_attacking


def check_check_2(
    current_board: classes.Board,
    coordinates: Tuple[classes.Coord, classes.Coord],
    places_attacking: List[classes.Coord],
    break_early: bool = False
):
    """Test if non-moved pieces can check king.

    Arguments:
        current_board {Board} -- current board
        coordinates {tuple[Coord]} -- old location of piece, king location
        places_attacking {list[Coord]} -- list of pieces currently checking king

    Keyword Arguments:
        break_early {bool} -- break after first check (default: {False})

    Returns:
        bool -- king in check
        list[Coord] -- pieces checking king
    """

    old_location, king_location = coordinates
    relative_move: classes.Coord = king_location-old_location
    absolute_move: classes.Coord = abs(relative_move)
    if absolute_move.x != absolute_move.y and min(absolute_move):
        return False, places_attacking
    king_direction = classes.Direction(relative_move)
    direction_of_attack = classes.Row(old_location, king_direction)
    attacking_color: classes.Color = current_board[king_location].COLOR.other
    current_pieces = current_board.playerpcs(attacking_color)
    pieces = (x for x in direction_of_attack if x in current_pieces)
    for x in pieces:
        try:
            move_check_2(current_board, (x, king_location))
        except classes.IllegalMove:
            continue
        else:
            places_attacking.append(x)
            if break_early or len(places_attacking) > 1:
                return True, places_attacking
            else:
                continue
    return False, places_attacking
