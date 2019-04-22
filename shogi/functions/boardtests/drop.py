from shogi import classes

from .mate import mate_check
from .move import is_movable

__all__ = [
    "is_legal_drop",
    "dropping_to_check",
]


def is_legal_drop(
        current_board: classes.Board,
        piece: classes.Piece,
        move_location: classes.AbsoluteCoord
):
    """Check if piece can be dropped in a location.

    :param current_board: current board state
    :param piece: piece to drop
    :param move_location: location to drop piece
    """
    # If there's a piece at the drop location, it's not valid
    if current_board[move_location]:
        return False
    player_int = int(current_board.current_player)
    must_promote = current_board.auto_promote(move_location, piece)
    # If the piece is dropped in a must-promote zone, it's not valid
    if must_promote:
        return False
    # Special pawn rules:
    if piece.has_type('p'):
        # No two pawns in the same column for the same player
        if any(x.is_piece('p', player_int)
               for x in current_board.column(move_location.y)):
            return False

        is_in_check = dropping_to_check(
            current_board,
            piece,
            move_location,
            current_board.current_player.other
        )
        # If the pawn is dropping to cause checkmate, not legal
        if is_in_check:
            # FIXME: Add before_move attribute to mate
            if mate_check(current_board, is_in_check):
                return False
    # Otherwise, yeah, it's fine
    return True


def dropping_to_check(
        current_board: classes.Board,
        piece_to_drop: classes.Piece,
        new_location: classes.AbsoluteCoord,
        king_color: classes.Color
) -> classes.CoordSet:
    """Test if dropped piece is checking king.

    :param current_board: current board state
    :param piece_to_drop: piece to drop
    :param new_location: location to drop piece at
    :param king_color: color of king to attack
    """
    king_location = current_board.get_king(king_color)
    places_attacking = set()
    # If the piece can attack the king, it's check.
    # Otherwise, no other pieces have had a path to the king
    # magically opened up, so there's no check
    if is_movable(
            current_board,
            (new_location, king_location),
            act_full=new_location,
            piece_pretend=piece_to_drop
    ):
        places_attacking.add(new_location)
    return places_attacking
