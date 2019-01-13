from typing import List, Tuple

from shogi import classes

from .move import move_check_2

__all__ = [
    "check_check",
    "check_check_2"
]


def check_check(
        current_board: classes.Board,
        coordinates: Tuple[classes.AbsoluteCoord, classes.AbsoluteCoord],
        king_color: classes.Color,
        break_early: bool = False,
        before_move: bool = False
) -> Tuple[classes.AbsoluteCoord, List[classes.AbsoluteCoord]]:
    """Find if king is in check.

    :param current_board: current game board
    :param coordinates: last move (from, to)
    :param king_color: color of king to test
    :param break_early: break after first finding of check
    :param before_move: whether or not the move has been made
    :return: location of king, list of coordinates attacking king
    """

    old_location, new_location = coordinates
    places_attacking: List[classes.AbsoluteCoord] = []
    king_tested: classes.Piece = classes.Piece('k', king_color)
    king_location: classes.AbsoluteCoord = current_board.get_piece(king_tested)
    try:
        if before_move:
            move_check_2(
                current_board,
                (new_location, king_location),
                ignore_location=old_location,
                act_full=new_location
            )
        else:
            move_check_2(current_board, (new_location, king_location))
    except classes.IllegalMove:
        places_attacking = check_check_2(
            current_board,
            (old_location, new_location),
            king_location,
            places_attacking,
            break_early,
            before_move
        )
    else:
        if break_early:
            places_attacking.append(new_location)
            return king_location, places_attacking
        else:
            places_attacking.append(new_location)
            places_attacking = check_check_2(
                current_board,
                (old_location, new_location),
                king_location,
                places_attacking,
                break_early,
                before_move
            )
            return king_location, places_attacking
    return king_location, places_attacking


def check_check_2(
        current_board: classes.Board,
        coordinates: Tuple[classes.AbsoluteCoord, classes.AbsoluteCoord],
        king_location: classes.AbsoluteCoord,
        places_attacking: List[classes.AbsoluteCoord],
        break_early: bool = False,
        before_move: bool = False
) -> List[classes.AbsoluteCoord]:
    """Test if non-moved pieces can check king.

    :param current_board: current board
    :param coordinates: last move (from, to)
    :param king_location: location of king to test
    :param places_attacking: list of places currently checking king
    :param break_early: break after first check
    :return: pieces checking king
    """

    old_location, new_location = coordinates
    relative_move = classes.RelativeCoord(king_location - old_location)
    absolute_move: classes.RelativeCoord = abs(relative_move)
    if absolute_move.x != absolute_move.y and min(absolute_move):
        return places_attacking
    king_direction = classes.Direction(relative_move)
    direction_of_attack = classes.Row(old_location, king_direction)
    attacking_color: classes.Color = current_board[king_location].color.other
    current_pieces = current_board.player_pieces(attacking_color)
    pieces = (x for x in direction_of_attack if x in current_pieces)
    for x in pieces:
        try:
            if before_move:
                move_check_2(
                    current_board,
                    (x, king_location),
                    ignore_location=old_location,
                    act_full=new_location
                )
            else:
                move_check_2(current_board, (x, king_location))
        except classes.IllegalMove:
            continue
        else:
            places_attacking.append(x)
            if break_early or len(places_attacking) > 1:
                return places_attacking
            else:
                continue
    return places_attacking
