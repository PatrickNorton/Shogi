from itertools import product
from shogi import classes
from .goodinput import input_piece
from typing import Tuple

__all__ = [
    "move_check",
    "move_check_2",
    "obstruction_check",
    "king_check"
]


def move_check(
        current_location: classes.Coord,
        move_string: str
) -> Tuple[classes.Coord, classes.Coord]:
    """Check if inputted piece is a valid piece

    TODO: deprecate this in favor of direct input_piece call

    Arguments:
        current_location {Coord} -- position of piece to be moved
        move_string {str} -- input of piece to be moved

    Raises:
        classes.IllegalMove -- invalid entry

    Returns:
        tuple[Coord] -- coords of movement
    """

    valid_piece = input_piece(move_string)
    if not valid_piece:
        raise classes.IllegalMove(11)
    move_location = classes.Coord(move_string)
    return current_location, move_location


def move_check_2(
    current_board: classes.Board,
    coordinates: Tuple[classes.Coord, classes.Coord]
):
    """Check if piece can be moved between locations.

    Arguments:
        current_board {Board} -- current board state
        coordinates {tuple[Coord]} -- current and new locations of piece

    Raises:
        classes.IllegalMove -- attempted zero-move of piece
        classes.IllegalMove -- move to illegal location
        classes.IllegalMove -- capture of own piece
    """

    current, new = coordinates
    piece = current_board[current]
    move = new-current
    move_direction = classes.Direction(move)
    move_variable = piece.MOVES[move_direction]
    if move_direction == classes.Direction(8):
        raise classes.IllegalMove(3)
    elif not piece.canmove(move):
        raise classes.IllegalMove(1)
    elif current_board[new].samecolor(current_board[current]):
        raise classes.IllegalMove(4)
    elif move_variable == 'T':
        pass
    elif piece.hastype('k'):
        king_check(current_board, (current, new))
    else:
        obstruction_check(current_board, current, move)


def obstruction_check(current_board, current_position, move_position):
    """Check if piece is obstructing move_position.

    Arguments:
        current_board {Board} -- current_position board state
        current_position {Coord} -- current_position piece location
        move_position {Coord} -- location to move_position piece

    Raises:
        classes.IllegalMove -- obstruction found
    """
    # TODO: Type hints

    move_direction = classes.Direction(move_position)
    for x in range(1, max(abs(move_position))):
        relative_position = [x*k for k in move_direction]  # TODO: Change to Coord
        test_position = current_position + classes.Coord(relative_position)
        if current_board[test_position]:
            raise classes.IllegalMove(2)


def king_check(current_board, coordinates):
    """Check if king is moving into check.

    Arguments:
        current_board {Board} -- current board state
        coordinates {tuple[Coord]} -- current and new piece location

    Raises:
        classes.IllegalMove -- attempted capture of own piece
        classes.IllegalMove -- attempted move into check
        classes.IllegalMove -- attempted move into check
    """

    # TODO: Type hints

    old_location, new_location = coordinates
    direction_set = (classes.Direction(x) for x in range(8))
    for direction, distance in product(direction_set, range(9)):
        distance = classes.Coord(distance)
        try:
            current_test = new_location+direction*distance
            if current_board[current_test].samecolor(current_board[old_location]):
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
        relative_position = classes.Coord((move_x, 2*move_y))
        try:
            absolute_position = new_location+relative_position
            move_check_2(current_board, (absolute_position, new_location))
        except (ValueError, IndexError):
            continue
        except classes.IllegalMove:
            continue
        else:
            raise classes.IllegalMove(6)
