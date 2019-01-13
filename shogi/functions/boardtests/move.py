from itertools import product
from typing import Tuple

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
) -> Tuple[classes.AbsoluteCoord, classes.AbsoluteCoord]:
    """Check if inputted piece is a valid piece.

    :param current_location: position of piece to be moved
    :param move_string:  input of piece to be moved
    :raises classes.IllegalMove: invalid entry
    :return: coordinates of movement
    """

    valid_piece = input_piece(move_string)
    if not valid_piece:
        raise classes.IllegalMove(11)
    move_location = classes.AbsoluteCoord(move_string)
    return current_location, move_location


def move_check_2(
        current_board: classes.Board,
        coordinates: Tuple[classes.AbsoluteCoord, classes.AbsoluteCoord],
        ignore_location: classes.AbsoluteCoord = None,
        act_full: classes.AbsoluteCoord = None
):
    """Check if piece can be moved between locations.

    :param current_board: current board state
    :param coordinates: current and new locations of piece
    :param ignore_location: location to ignore for obstruction check
    :param act_full: location to pretend is full
    :raises classes.IllegalMove: attempted 0-move of piece
    :raises classes.IllegalMove: move to illegal location
    :raises classes.IllegalMove: capture of own piece
    """

    current, new = coordinates
    piece = current_board[current]
    move = new - current
    move_direction = classes.Direction(move)
    move_variable = piece.moves[move_direction]
    if move_direction == classes.Direction(8):
        raise classes.IllegalMove(3)
    elif not piece.can_move(move):
        raise classes.IllegalMove(1)
    elif current_board[new].same_color(current_board[current]):
        raise classes.IllegalMove(4)
    elif move_variable == 'T':
        pass
    elif piece.has_type('k'):
        king_check(current_board, (current, new))
    else:
        obstruction_check(
            current_board,
            current,
            move,
            ignore_location,
            act_full
        )


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
            raise classes.IllegalMove(2)
        if test_position == act_full:
            raise classes.IllegalMove(2)


def king_check(
        current_board: classes.Board,
        coordinates: Tuple[classes.AbsoluteCoord, classes.AbsoluteCoord]
):
    """Check if king is moving into check.

    :param current_board: current board state
    :param coordinates: current and new piece location
    :raises classes.IllegalMove: attempted capture of piece
    :raises classes.IllegalMove: attempted move into check
    :raises classes.IllegalMove: attempted move into check
    """

    old_location, new_location = coordinates
    direction_set = (classes.Direction(x) for x in range(8))
    for direction, distance in product(direction_set, range(9)):
        distance = classes.AbsoluteCoord(distance)
        try:
            current_test = new_location + direction * distance
            if current_board[current_test].same_color(current_board[old_location]):
                raise classes.IllegalMove(4)
            move_check_2(current_board, (current_test, new_location))
        except (ValueError, IndexError):
            continue
        except classes.IllegalMove as e:
            if int(e) == '2':
                break
            else:
                continue
        else:
            raise classes.IllegalMove(6)
    for move_x, move_y in product((-1, 1), (-1, 1)):
        relative_position = classes.RelativeCoord((move_x, 2 * move_y))
        try:
            absolute_position = new_location + relative_position
            move_check_2(current_board, (absolute_position, new_location))
        except (ValueError, IndexError):
            continue
        except classes.IllegalMove:
            continue
        else:
            raise classes.IllegalMove(6)
