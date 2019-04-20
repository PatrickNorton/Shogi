from itertools import product
from typing import Set

from shogi import classes

__all__ = [
    "is_movable",
    "path_clear",
    "king_can_move",
]


def is_movable(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        ignore_locations: classes.CoordOrSet = frozenset(),
        act_full: classes.CoordOrSet = frozenset(),
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
    if isinstance(ignore_locations, classes.AbsoluteCoord):
        ignore_locations = {ignore_locations}
    if isinstance(act_full, classes.AbsoluteCoord):
        act_full = {act_full}
    if piece_pretend is None:
        piece = current_board[current]
    elif current in ignore_locations:
        piece = classes.NoPiece()
    else:
        piece = piece_pretend
    if act_full_pretend is not None and new in act_full:
        new_loc_piece = act_full_pretend
    else:
        new_loc_piece = current_board[new]
    move = new - current
    move_direction = classes.Direction(move)
    move_variable = piece.moves[move_direction]
    if move_direction == classes.Direction(8):
        return False
    elif not piece.can_move(move):
        return False
    elif new_loc_piece.same_color(piece):
        if new not in ignore_locations:
            return False
    elif isinstance(move_variable, list):
        pass
    elif piece.has_type('k') and with_king_check:
        return king_can_move(
            current_board, (current, new),
            ignore_locations=ignore_locations,
            act_full=act_full
        )
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
        ignore_locations: Set[classes.AbsoluteCoord] = frozenset(),
        act_full: Set[classes.AbsoluteCoord] = frozenset(),
) -> bool:
    """Check if piece is obstructing move.

    :param current_board: current board state
    :param current_position: current piece location
    :param move_position: location to move piece to
    :param ignore_locations: locations to ignore in check
    :param act_full: locations to pretend are full
    :raises classes.IllegalMove: obstruction found
    """

    move_direction = classes.Direction(move_position)
    for x in range(1, max(abs(move_position))):
        relative_position = classes.RelativeCoord(x) * move_direction
        test_position = current_position + relative_position
        if (current_board[test_position]
                and test_position not in ignore_locations):
            return False
        if test_position in act_full:
            return False
    return True


def king_can_move(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        ignore_locations: Set[classes.AbsoluteCoord] = frozenset(),
        act_full: Set[classes.AbsoluteCoord] = frozenset()
) -> bool:
    """Check if king is moving into check.

    :param current_board: current board state
    :param coordinates: current and new piece location
    :param ignore_locations:
    :param act_full:
    """

    old_location, new_location = coordinates
    old_occupant = current_board[old_location]
    for direction in classes.Direction.valid():
        for distance in classes.RelativeCoord.positive_xy():
            try:
                current_test = classes.AbsoluteCoord(
                    new_location + direction * distance
                )
            except (ValueError, IndexError):
                break
            if current_board[current_test].same_color(old_occupant):
                break
            if current_board[current_test]:
                if is_movable(current_board,
                              (current_test, new_location),
                              ignore_locations={
                                  *ignore_locations, old_location
                              },
                              act_full={
                                  *act_full, new_location
                              }):
                    return False
                else:
                    break
    for move_x, move_y in product((-1, 1), (-1, 1)):
        relative_position = classes.RelativeCoord((move_x, 2 * move_y))
        try:
            absolute_position = classes.AbsoluteCoord(
                new_location + relative_position
            )
        except (ValueError, IndexError):
            continue
        if current_board[absolute_position].same_color(old_occupant):
            continue
        if is_movable(
                current_board,
                (absolute_position, new_location),
                ignore_locations=set(old_location),
                act_full=set(new_location)):
            return False
    return True


def into_check_check(
        current_board: classes.Board,
        coordinates: classes.AbsoluteCoord,
        king_color: classes.Color
) -> classes.CoordAndSet:
    old_location, new_location = coordinates
    places_attacking: classes.CoordSet = set()
    king_location: classes.AbsoluteCoord = current_board.get_king(king_color)
    kings_enemy = not current_board[old_location].is_color(king_color)
    if kings_enemy:
        if is_movable(current_board, (new_location, king_location),
                      ignore_locations=old_location,
                      act_full=new_location):
            places_attacking.add(new_location)
            return king_location, places_attacking
    relative_move = classes.RelativeCoord(king_location - old_location)
    absolute_move: classes.RelativeCoord = abs(relative_move)
    if not absolute_move.is_linear():
        return king_location, places_attacking
    king_direction = classes.Direction(relative_move)
    direction_of_attack = classes.Row(old_location, king_direction)
    attacking_color: classes.Color = current_board[king_location].color.other
    pieces = (x for x in direction_of_attack if x.is_color(attacking_color))
    for x in pieces:
        if is_movable(current_board, (x, king_location),
                      ignore_locations=old_location,
                      act_full=new_location):
            places_attacking.add(x)
            return king_location, places_attacking
