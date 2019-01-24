from typing import Set

from shogi import classes

from .mate import mate_check
from .move import move_check_2

__all__ = [
    "drop_check",
    "drop_check_check",
]


def drop_check(
        current_board: classes.Board,
        piece: classes.Piece,
        move_location: classes.AbsoluteCoord
):
    """Check if piece can be dropped in a location.

    :param current_board: current board state
    :param piece: piece to drop
    :param move_location: location to drop piece
    """
    if current_board[move_location]:
        return 1
    promotion_zones = ((0, 1, 2), (8, 7, 6))
    player_int = int(current_board.current_player)
    enemy_king = classes.Piece('k', current_board.current_player.other)
    king_location = current_board.get_piece(enemy_king)
    try:
        index = promotion_zones[player_int].index(move_location.y)
    except ValueError:
        pass
    else:
        if index < piece.auto_promote:
            return 1
    if piece.has_type('p'):
        space_row = classes.Row(move_location, 0)
        if any(current_board[x].is_piece('p', player_int) for x in space_row):
            return 1
        else:
            is_in_check = drop_check_check(
                current_board,
                piece,
                move_location,
                current_board.current_player.other
            )
            if is_in_check:
                # FIXME: Add before_move attribute to mate
                is_mate = mate_check(
                    current_board,
                    king_location,
                    is_in_check
                )
                if is_mate:
                    return 1


def drop_check_check(
        current_board: classes.Board,
        piece_to_drop: classes.Piece,
        new_location: classes.AbsoluteCoord,
        king_color: classes.Color
) -> Set[classes.AbsoluteCoord]:
    """Test if dropped piece is checking king.

    :param current_board: current board state
    :param piece_to_drop: piece to drop
    :param new_location: location to drop piece at
    :param king_color: color of king to attack
    """
    king_location = current_board.get_piece(classes.Piece('k', king_color))
    places_attacking = set()
    cannot_move = move_check_2(
        current_board,
        (new_location, king_location),
        act_full=new_location,
        piece_pretend=piece_to_drop
    )
    if not cannot_move:
        places_attacking.add(new_location)
    return places_attacking
