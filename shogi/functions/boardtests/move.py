from collections import Generator
from itertools import product

from shogi import classes

__all__ = [
    "is_movable",
    "path_clear",
    "king_can_move",
]


def is_movable(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        ignore_locations: classes.CoordIter = (),
        act_full: classes.CoordIter = (),
        piece_pretend: classes.Piece = None,
        act_full_pretend: classes.Piece = None,
        with_king_check: bool = True,
) -> bool:
    """Check if piece can be moved between locations.

    :param current_board: current board state
    :param coordinates: current and new locations of piece
    :param ignore_locations: location to ignore for obstruction check
    :param act_full: location to pretend is full
    :param piece_pretend: piece to pretend is moving
    :param act_full_pretend: piece to pretend is in the act_full loc
    :param with_king_check: whether or not king_can_move should be run
    :return: error code
    """
    current, new = coordinates
    if isinstance(ignore_locations, Generator):
        ignore_locations = set(ignore_locations)
    if isinstance(act_full, Generator):
        act_full = set(act_full)
    # Figure out what the moved piece is
    # If the place the piece is is in ignore_locations, then we
    # pretend the space is empty
    if current in ignore_locations:
        piece = classes.NoPiece()
    # If we're not pretending anything, then it's the piece at the
    # location it's moving from
    elif piece_pretend is None:
        piece = current_board[current]
    # Otherwise, it's the piece we're pretending it is
    else:
        piece = piece_pretend
    # Figure out what the piece in the location we're moving to
    # is
    # If act_full_pretend exists, and the new space is one of the ones
    # we're pretending is full, then the piece in the new location is
    # the one we're pretending it is
    if act_full_pretend is not None and new in act_full:
        new_loc_piece = act_full_pretend
    # Otherwise, it's what the piece at the new space actually is
    else:
        new_loc_piece = current_board[new]
    move = current.distance_to(new)
    move_direction = classes.Direction(move)
    # If the move is a null move, it's not valid
    if move_direction == classes.Direction(8):
        return False
    # If the move isn't in a legal direction for the piece, it's not
    # valid
    elif not piece.can_move(move):
        return False
    # If the piece in the new location is the same color as the piece,
    # then you can't move there (no capturing your own piece), as long
    # as the space isn't one of the ones we're ignoring
    elif new_loc_piece.same_color(piece) and new not in ignore_locations:
            return False
    # If the piece is moving different different amounts in the x and
    # y directions, then it's un-block-able, and we shouldn't test to
    # see if a piece is in the way (for example, knights)
    elif not move.is_linear:
        pass
    # If the piece is a king, and we are running king_check, check
    # whether or not the king can move
    elif piece.is_rank('k') and with_king_check:
        return king_can_move(
            current_board, (current, new),
            ignore_locations=ignore_locations,
            act_full=act_full
        )
    # Otherwise, return whether or not the path is clear
    else:
        return path_clear(
            current_board,
            current,
            move,
            ignore_locations=ignore_locations,
            act_full=act_full
        )
    return True


def path_clear(
        current_board: classes.Board,
        current_position: classes.AbsoluteCoord,
        move_position: classes.AbsoluteCoord,
        ignore_locations: classes.CoordIter = (),
        act_full: classes.CoordIter = (),
) -> bool:
    """Check if piece is obstructing move.

    :param current_board: current board state
    :param current_position: current piece location
    :param move_position: location to move piece to
    :param ignore_locations: locations to ignore in check
    :param act_full: locations to pretend are full
    :return: whether or not hte path is clear
    """
    move_direction = classes.Direction(move_position)
    if isinstance(ignore_locations, Generator):
        ignore_locations = set(ignore_locations)
    if isinstance(act_full, Generator):
        act_full = set(act_full)
    # For each square upto the move_position's maximum value:
    # Max is needed to get the actual amount of spaces the move
    # traverses, to test each space in between.
    for x in range(1, max(abs(move_position))):
        # The relative move amount is the direction of the move
        # times the number of squares from the start that is being
        # tested this time
        relative_position = move_direction.scale(x)
        test_position = current_position + relative_position
        # If there's a piece at the test position, and we're not
        # ignoring it, then there's a piece in the way and the path
        # is therefore not clear
        if (current_board[test_position]
                and test_position not in ignore_locations):
            return False
        # If we're pretending the test position is full, then there's
        # a piece in the way
        if test_position in act_full:
            return False
    # If there's no pieces in the way, the path is clear
    return True


def king_can_move(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        ignore_locations: classes.CoordIter = frozenset(),
        act_full: classes.CoordIter = frozenset()
) -> bool:
    """Check if king is moving into check.

    :param current_board: current board state
    :param coordinates: current and new piece location
    :param ignore_locations: spaces to pretend are empty
    :param act_full: spaces to pretend are full
    """
    old_location, new_location = coordinates
    old_occupant = current_board[old_location]
    # Test in each direction radiating out from the king, testing
    # each distance from the king starting at 1.
    for direction in classes.Direction.valid():
        # Test for each distance away from the king
        for distance in classes.RelativeCoord.positive_xy():
            # If we've moved off the board, stop testing in this
            # direction
            try:
                current_test = new_location + direction.scale(distance)
            except ValueError:
                break
            # If there's a piece on the path, and it has the same
            # color as the king, then stop testing in this direction
            if current_board[current_test].same_color(old_occupant):
                break
            if current_board[current_test]:
                # If the piece at this location can attack the king,
                # then the king is moving into check, and thus cannot
                # move to where it is
                if is_movable(
                        current_board,
                        (current_test, new_location),
                        ignore_locations={*ignore_locations, old_location},
                        act_full={*act_full, new_location}
                ):
                    return False
                # Otherwise, there's a piece in the direction we're
                # testing, and thus we shouldn't continue, because all
                # the pieces we test from here on out will fail the
                # obstruction check
                else:
                    break
    # Test the knight's moves
    for move_x, move_y in product((-1, 1), (-1, 1)):
        # For each space two y-coords away and 1 x-coord (knight's
        # move):
        relative_position = classes.RelativeCoord((move_x, 2 * move_y))
        # If the tested location isn't on the board, don't test it
        try:
            absolute_position = new_location + relative_position
        except ValueError:
            continue
        # If the piece at the tested location is the same color as the
        # king, then it can't move there
        if current_board[absolute_position].same_color(old_occupant):
            continue
        # If any piece can move to where the king is, then it's check
        # and the king can't move there
        if is_movable(
                current_board,
                (absolute_position, new_location),
                ignore_locations={old_location},
                act_full={new_location}
        ):
            return False
    return True
