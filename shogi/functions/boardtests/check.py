from shogi import classes
from .drop import dropping_to_check
from .move import is_movable

__all__ = [
    "is_check",
    "unmoved_can_check",
]


def is_check(
        current_board: classes.Board,
        coordinates: classes.OptCoordTuple,
        king_color: classes.Color,
        break_early: bool = False,
        before_move: bool = False,
        dropped_piece: classes.Piece = None
) -> classes.CoordSet:
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
        checking_spaces = dropping_to_check(
            current_board,
            dropped_piece,
            new_location,
            king_color
        )
        return checking_spaces

    if before_move:
        kings_enemy = not current_board[old_location].is_color(king_color)
        if kings_enemy:
            can_move = is_movable(
                current_board,
                (new_location, king_location),
                ignore_locations=old_location,
                act_full=new_location
            )
        else:
            can_move = False
    else:
        can_move = is_movable(
            current_board,
            (new_location, king_location)
        )
    if can_move:
        places_attacking.add(new_location)
        if break_early:
            return places_attacking
    places_attacking = unmoved_can_check(
        current_board,
        (old_location, new_location),
        king_location,
        places_attacking,
        break_early=break_early,
        before_move=before_move
    )
    return places_attacking


def unmoved_can_check(
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
    pieces = (x for x in direction_of_attack
              if current_board[x].is_color(attacking_color))
    for x in pieces:
        if is_movable(
            current_board,
            (x, king_location),
            ignore_locations=old_location if before_move else None,
            act_full=new_location if before_move else None
        ):
            places_attacking.add(x)
            if break_early:
                return places_attacking
            else:
                continue
    return places_attacking
