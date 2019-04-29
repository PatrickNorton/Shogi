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
    # How this works:
    # There are four ways to get out of check: move, drop, capture,
    # and block.
    # This function tests if any is possible, in that order, as that
    # is the order of increasing difficulty,

    # If the king isn't in check, it isn't in checkmate
    if not places_attacking:
        return False
    # If no king_color was specified, default to the other color of
    # the first piece in places_attacking
    if king_color is None:
        # This weird construct is needed because there's no way to
        # get an item from a set non-destructively, so this has to be
        # used instead. Sigh.
        king_color = current_board[next(iter(places_attacking))].color.other
    king_location = current_board.king_loc(king_color)
    # Test if the king can move out of check
    for king_move_tested in current_board[king_location].valid_spaces:
        # For each space in the king's valid moves, test if the king
        # is able to move there or not
        try:
            new_location = king_location + king_move_tested
        # If the coordinate isn't legal, the piece can't move there,
        # so move on
        except ValueError:
            continue
        # If the king can move to the new location, congrats! It's not
        # in check
        if is_movable(current_board, (king_location, new_location)):
            return False
    # If there's more than one piece attacking, you can't block
    # or capture, so resistance is futile
    if len(places_attacking) > 1:
        return True
    # Since there's only one location in pieces_attacking, we can
    # just get it and use it directly
    check_location = places_attacking.pop()
    relative_position = check_location.distance_to(king_location)
    # Test whether a drop is legal first
    # If the player has no pieces to drop, they can't drop to block
    has_pieces = current_board.captured[current_board.current_player]
    # If the piece is a knight, it can't be blocked
    not_a_knight = not current_board[check_location].is_rank('n')
    # If the piece is right next to the king, you can't put a piece
    # between it and the king to block it
    has_space = not all(x in {-1, 0, 1} for x in relative_position)
    # If all of these drop-tests are true, it can be blocked
    if has_pieces and not_a_knight and has_space:
        return False
    # Test whether or not the attacking piece can be captured
    for loc in current_board.enemy_spaces:
        # See if any piece can be moved to the attacking location,
        # to capture the piece
        if is_movable(current_board, (loc, check_location)):
            return False
    move = king_location - check_location
    move_direction = classes.Direction(move)
    # Test whether or not the piece can be blocked
    # If those tests we saw earlier are false, you can't block the
    # check, and thus, checkmate is true
    if not (not_a_knight and has_space):
        return True
    # Test if any of the player's pieces can move to any of the
    # spaces between the attacking piece and the king
    for pos, z in product(current_board.enemy_spaces, range(max(abs(move)))):
        # The location the piece is moving to:
        # The location the piece is moving from, plus
        # z times the move direction, e.g. z spaces away from
        # the check location in the direction of the move
        new_location = (check_location + move_direction.scale(z))
        # If you can move there and block, no checkmate
        if is_movable(current_board, (pos, new_location)):
            return False
    # If nothing says there isn't checkmate, then there is
    return True
