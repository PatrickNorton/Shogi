from shogi import classes
from .drop import drop_check_check
from .move import move_check_2

__all__ = [
    "check_check",
    "check_check_2"
]


def check_check(
        current_board: classes.Board,
        coordinates: classes.OptCoordTuple,
        king_color: classes.Color,
        break_early: bool = False,
        before_move: bool = False,
        dropped_piece: classes.Piece = None
) -> classes.CoordAndSet:
    """Find if king is in check.

    :param current_board: current game board
    :param coordinates: last move (from, to)
    :param king_color: color of king to test
    :param break_early: break after first finding of check
    :param before_move: whether or not the move has been made
    :param dropped_piece: piece to be dropped
    :return: location of king, list of coordinates attacking king
    """

    old_location, new_location = coordinates
    places_attacking: classes.CoordSet = set()
    king_location: classes.AbsoluteCoord = current_board.get_king(king_color)

    if dropped_piece is not None:
        checking_spaces = drop_check_check(
            current_board,
            dropped_piece,
            new_location,
            king_color
        )
        return king_location, checking_spaces

    if before_move:
        kings_enemy = not current_board[old_location].is_color(king_color)
        if kings_enemy:
            cannot_move = move_check_2(
                current_board,
                (new_location, king_location),
                ignore_location=old_location,
                act_full=new_location
            )
        else:
            cannot_move = 4
    else:
        cannot_move = move_check_2(
            current_board,
            (new_location, king_location)
        )
    if not cannot_move:
        places_attacking.add(new_location)
        if break_early:
            return king_location, places_attacking
    places_attacking = check_check_2(
        current_board,
        (old_location, new_location),
        king_location,
        places_attacking,
        break_early=break_early,
        before_move=before_move
    )
    return king_location, places_attacking


def check_check_2(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        king_location: classes.AbsoluteCoord,
        places_attacking: classes.CoordSet,
        break_early: bool = False,
        before_move: bool = False
) -> classes.CoordSet:
    """Test if non-moved pieces can check king.

    :param current_board: current board
    :param coordinates: last move (from, to)
    :param king_location: location of king to test
    :param places_attacking: list of places currently checking king
    :param break_early: break after first check
    :param before_move: if move has yet been made
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
    pieces = (x for x in direction_of_attack if current_board[x].is_color(attacking_color))
    for x in pieces:
        if before_move:
            cannot_move = move_check_2(
                current_board,
                (x, king_location),
                ignore_location=old_location,
                act_full=new_location
            )
        else:
            cannot_move = move_check_2(current_board, (x, king_location))
        if cannot_move:
            continue
        else:
            places_attacking.add(x)
            if break_early:
                return places_attacking
            else:
                continue
    return places_attacking
