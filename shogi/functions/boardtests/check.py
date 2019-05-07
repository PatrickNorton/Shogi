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
    :return: set of coordinates attacking king
    """
    old_location, new_location = coordinates
    places_attacking: classes.CoordSet = set()
    king_location: classes.AbsoluteCoord = current_board.king_loc(king_color)
    # If there is a dropped piece, delegate to dropping_to_check
    if dropped_piece is not None:
        return dropping_to_check(
            current_board,
            dropped_piece,
            new_location,
            king_color
        )
    # If the move hasn't been made yet, run is_movable with the old
    # and new locations pretended as full/empty
    if before_move:
        can_move = is_movable(
            current_board,
            (new_location, king_location),
            ignore_locations={old_location},
            act_full={new_location}
        )
    # If the move has been made, proceed as normal
    # Test if the piece moved can attack the king itself
    else:
        can_move = is_movable(
            current_board,
            (new_location, king_location)
        )
    # If the piece can attack the king, add its location to
    # pieces_attacking, and return if break_early is True
    if can_move:
        places_attacking.add(new_location)
        if break_early:
            return places_attacking
    # Figure out if any of the unmoved pieces can attack the king
    return unmoved_can_check(
        current_board,
        (old_location, new_location),
        king_location,
        places_attacking,
        break_early=break_early,
        before_move=before_move
    )


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
    # The logic behind the magic:
    # The only two spaces on the board that actually change are the
    # location the piece moved from and the place it moved to.
    # Given this, the only pieces that can check the king that
    # couldn't already are the ones whose move towards the king goes
    # through the only space that wasn't free, and now is, e.g. the
    # old location of the moved piece.
    #
    # Therefore, to find which pieces check the king, one only needs
    # to check along the row between the original location of the
    # piece and the location of the king for pieces that can attack.
    # Knights' moves do not need to be checked, because knights can
    # jump over pieces, and therefore, if a knight can attack the king
    # now, it could already.

    old_location, new_location = coordinates
    relative_move = old_location.distance_to(king_location)
    # If there is not a linear move from the old location to the
    # king's location, then the no pieces can go through that newly-
    # freed spot to attack the king, therefore the piece didn't unblock
    # anything, and therefore, no pieces can check the king.
    if not relative_move.is_linear:
        return places_attacking
    king_direction = classes.Direction(relative_move)
    direction_of_attack = classes.Row(old_location, king_direction)
    attacking_color: classes.Color = current_board[king_location].color.other
    pieces = (x for x in direction_of_attack
              if current_board[x].is_color(attacking_color))
    # Iterate along the row between the original space and the king's,
    # checking if any pieces can move there.
    for x in pieces:
        if is_movable(
            current_board,
            (x, king_location),
            ignore_locations={old_location} if before_move else set(),
            act_full={new_location} if before_move else set()
        ):
            places_attacking.add(x)
            # Return the set of places attacking if break_early is True
            if break_early:
                return places_attacking
    return places_attacking
