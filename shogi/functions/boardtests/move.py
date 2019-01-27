from itertools import product

from shogi import classes
from .goodinput import input_piece

__all__ = [
    "move_check",
    "move_check_2",
    "obstruction_check",
    "king_check"
]


def move_check(
        current_location: classes.AbsoluteCoord,
        move_string: str
) -> classes.CoordTuple:
    """Check if inputted piece is a valid piece.

    :param current_location: position of piece to be moved
    :param move_string:  input of piece to be moved
    :raises classes.IllegalMove: invalid entry
    :return: coordinates of movement
    """

    valid_piece = input_piece(move_string)
    if not valid_piece:
        raise ValueError
    move_location = classes.AbsoluteCoord(move_string)
    return current_location, move_location


def move_check_2(
        current_board: classes.Board,
        coordinates: classes.CoordTuple,
        ignore_location: classes.AbsoluteCoord = None,
        act_full: classes.AbsoluteCoord = None,
        piece_pretend: classes.Piece = None,
        act_full_pretend: classes.Piece = None
) -> int:
    """Check if piece can be moved between locations.

    :param current_board: current board state
    :param coordinates: current and new locations of piece
    :param ignore_location: location to ignore for obstruction check
    :param act_full: location to pretend is full
    :param piece_pretend: piece to pretend is moving
    :param act_full_pretend: piece to pretend is in the act_full loc
    :return: error code
    """

    current, new = coordinates
    if piece_pretend is None:
        piece = current_board[current]
    else:
        piece = piece_pretend
    if act_full_pretend is not None and act_full == new:
        new_loc_piece = act_full_pretend
    else:
        new_loc_piece = current_board[new]
    move = new - current
    move_direction = classes.Direction(move)
    move_variable = piece.moves[move_direction]
    if move_direction == classes.Direction(8):
        return 3
    elif not piece.can_move(move):
        return 1
    elif new_loc_piece.same_color(piece):
        if new != ignore_location:
            return 4
    elif move_variable == 'T':
        pass
    elif piece.has_type('k'):
        return king_check(current_board, (current, new))
    else:
        return obstruction_check(
            current_board,
            current,
            move,
            ignore_location,
            act_full
        )
    return 0


def obstruction_check(
        current_board: classes.Board,
        current_position: classes.AbsoluteCoord,
        move_position: classes.AbsoluteCoord,
        ignore_location: classes.AbsoluteCoord = None,
        act_full: classes.AbsoluteCoord = None,
):
    """Check if piece is obstructing move.

    :param current_board: current board state
    :param current_position: current piece location
    :param move_position: location to move piece to
    :param ignore_location: location to ignore in check
    :param act_full: location to pretend is full
    :raises classes.IllegalMove: obstruction found
    """

    move_direction = classes.Direction(move_position)
    for x in range(1, max(abs(move_position))):
        relative_position = classes.RelativeCoord(x) * move_direction
        test_position = current_position + relative_position
        if current_board[test_position] and test_position != ignore_location:
            return 2
        if test_position == act_full:
            return 2
    return 0


def king_check(
        current_board: classes.Board,
        coordinates: classes.CoordTuple
):
    """Check if king is moving into check.

    :param current_board: current board state
    :param coordinates: current and new piece location
    :raises classes.IllegalMove: attempted capture of piece
    :raises classes.IllegalMove: attempted move into check
    :raises classes.IllegalMove: attempted move into check
    """

    old_location, new_location = coordinates
    old_occupant = current_board[old_location]
    for direction, distance in product(classes.Direction.valid(), range(9)):
        distance = classes.AbsoluteCoord(distance)
        try:
            current_test = new_location + direction * distance
        except (ValueError, IndexError):
            continue
        else:
            if isinstance(current_test, classes.RelativeCoord):
                continue
            if current_board[current_test].same_color(old_occupant):
                continue
            cannot_move = move_check_2(
                current_board,
                (current_test, new_location),
                ignore_location=old_location,
                act_full=new_location,
            )
            if cannot_move == 2:
                break
            elif cannot_move:
                continue
            else:
                return 6
    for move_x, move_y in product((-1, 1), (-1, 1)):
        relative_position = classes.RelativeCoord((move_x, 2 * move_y))
        try:
            absolute_position = new_location + relative_position
        except (ValueError, IndexError):
            continue
        else:
            if isinstance(absolute_position, classes.RelativeCoord):
                continue
            if current_board[absolute_position].same_color(old_occupant):
                continue
            cannot_move = move_check_2(
                current_board,
                (absolute_position, new_location),
                ignore_location=old_location,
                act_full=new_location,
            )
            if cannot_move:
                continue
            else:
                return 6
    return 0


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
        cannot_move = move_check_2(
            current_board,
            (new_location, king_location),
            ignore_location=old_location,
            act_full=new_location
        )
        if not cannot_move:
            places_attacking.add(new_location)
            return king_location, places_attacking
    relative_move = classes.RelativeCoord(king_location - old_location)
    absolute_move: classes.RelativeCoord = abs(relative_move)
    if absolute_move.x != absolute_move.y and min(absolute_move):
        return king_location, places_attacking
    king_direction = classes.Direction(relative_move)
    direction_of_attack = classes.Row(old_location, king_direction)
    attacking_color: classes.Color = current_board[king_location].color.other
    pieces = (x for x in direction_of_attack if x.is_color(attacking_color))
    for x in pieces:
        cannot_move = move_check_2(
            current_board,
            (x, king_location),
            ignore_location=old_location,
            act_full=new_location,
        )
        if not cannot_move:
            places_attacking.add(x)
            return king_location, places_attacking
