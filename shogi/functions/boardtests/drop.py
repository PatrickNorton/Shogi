from shogi import classes

from .mate import mate_check
from .move import move_check_2

__all__ = [
    "drop_check"
]


def drop_check(current_board, piece, move_location):
    if current_board[move_location]:
        raise classes.IllegalMove
    promotion_zones = ((0, 1, 2), (8, 7, 6))
    player_int = int(current_board.current_player)
    try:
        index = promotion_zones[player_int].index(move_location.y)
    except ValueError:
        pass
    else:
        if index < piece.auto_promote:
            raise classes.IllegalMove
    if piece.has_type('p'):
        current_row = classes.Row(move_location, 0)
        if any(current_board[x].is_piece('p', player_int) for x in current_row):
            raise classes.IllegalMove
        else:
            is_in_check = foo(
                current_board,
                piece,
                move_location,
                current_board.current_player.other
            )
            if is_in_check:
                # FIXME: Add before_move attribute to mate
                is_mate = mate_check(
                    current_board,
                    current_board.get_piece(classes.Piece('k', current_board.current_player.other)),
                    is_in_check
                )
                if is_mate:
                    raise classes.IllegalMove


def foo(current_board, piece_to_drop, new_location, king_color):
    king_location = current_board.get_piece(classes.Piece('k', king_color))
    places_attacking = []
    try:
        move_check_2(
            current_board,
            (new_location, king_location),
            act_full=new_location,
            piece_pretend=piece_to_drop
        )
    except classes.IllegalMove:
        return []
    else:
        places_attacking.append(new_location)
        return places_attacking
