from itertools import product

from typing import Iterable, Generator

from shogi import classes
from .move import is_movable

__all__ = [
    "mate_check",
]


def mate_check(
        current_board: classes.Board,
        places_attacking: classes.CoordSet,
        king_color: classes.Color = None,
        ignore_locations: Iterable[classes.Piece] = frozenset(),
        act_full: Iterable[classes.Piece] = frozenset(),
        piece_pretend: classes.Piece = None,
) -> bool:
    """Test if king is in checkmate.

    :param current_board: Current board state
    :param places_attacking: set of pieces attacking the king
    :param king_color: Color of king to see if is in checkmate
    :param ignore_locations: spaces to pretend are empty
    :param act_full: spaces to pretend are full
    :param piece_pretend: piece to pretend these spaces are
    :return: if king is in checkmate
    """
    # How this works:
    # There are four ways to get out of check: move, drop, capture,
    # and block.
    # This function tests if any is possible, in that order, as that
    # is the order of increasing difficulty,

    # Generator guards
    if isinstance(ignore_locations, Generator):
        ignore_locations = set(ignore_locations)
    if isinstance(act_full, Generator):
        act_full = set(act_full)
    # If the king isn't in check, it isn't in checkmate
    if not places_attacking:
        return False
    # If no king_color was specified, default to the other color of
    # the first piece in places_attacking
    if king_color is None:
        # Get the color of the attacking piece, but if there is not
        # yet a piece at the space, for example, if the move hasn't
        # happened yet, then we check if there is a piece at the
        # pretended location.
        # If there is, then we get its color, if specified.
        # Otherwise, we move on to the next space.
        for space in places_attacking:
            piece = current_board[space]
            if piece:
                king_color = piece.color.other
                break
            else:
                if piece in ignore_locations and piece_pretend:
                    king_color = piece_pretend.color.other
                    break
        # If no reasonable color is found, then something has gone
        # badly wrong, and the program should fail.
        else:
            raise ValueError("No color for the attacking king could be found")
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
        if is_movable(
                current_board, (king_location, new_location),
                ignore_locations=ignore_locations,
                act_full=act_full,
                piece_pretend=piece_pretend
        ):
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
    has_space = abs(relative_position.x) > 1 or abs(relative_position.y) > 1
    # If all of these drop-tests are true, it can be blocked
    if has_pieces and not_a_knight and has_space:
        return False
    # Test whether or not the attacking piece can be captured
    for loc in current_board.enemy_spaces:
        # See if any piece can be moved to the attacking location,
        # to capture the piece
        if is_movable(
                current_board, (loc, check_location),
                ignore_locations=ignore_locations,
                act_full=act_full,
                piece_pretend=piece_pretend
        ):
            return False
    move = king_location - check_location
    move_direction = classes.Direction(move)
    # Test whether or not the piece can be blocked
    # If those tests we saw earlier are false, you can't block the
    # check, and thus, checkmate is true
    if not not_a_knight or not has_space:
        return True
    # Test if any of the player's pieces can move to any of the
    # spaces between the attacking piece and the king
    for pos, z in product(current_board.enemy_spaces, range(max(abs(move)))):
        # The location the piece is moving to:
        #   The location the piece is moving from, plus z spaces away
        #   from the location on the direction of the move
        new_location = check_location + move_direction.scale(z)
        # If you can move there and block, no checkmate
        if is_movable(current_board, (pos, new_location),
                      ignore_locations=ignore_locations,
                      act_full=act_full,
                      piece_pretend=piece_pretend):
            return False
    # If nothing says there isn't checkmate, then there is
    return True
