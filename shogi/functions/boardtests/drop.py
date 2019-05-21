from typing import Iterable, Generator

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
        move_location: classes.AbsoluteCoord,
        checking_spaces: Iterable[classes.AbsoluteCoord] = frozenset(),
):
    """Check if piece can be dropped in a location.

    :param current_board: current board state
    :param piece: piece to drop
    :param move_location: location to drop piece
    :param checking_spaces: spaces checking the king
    """
    if isinstance(checking_spaces, Generator):
        checking_spaces = set(checking_spaces)
    # If there is more than one piece checking the king, then they
    # can't bw blocked, and thus the move is invalid
    if len(checking_spaces) > 1:
        return False
    # If there's a piece at the drop location, it's not valid
    if current_board[move_location]:
        return False
    player_int = int(current_board.current_player)
    must_promote = current_board.auto_promote(move_location, piece)
    # If the piece is dropped in a must-promote zone, it's not valid
    if must_promote:
        return False
    # Special pawn rules:
    if piece.is_rank('p'):
        # No two pawns in the same column for the same player
        for x in current_board.column(move_location.y):
            if x.is_piece('p', player_int):
                return False
        # Get all the spaces checking the king
        is_checking = dropping_to_check(
            current_board,
            piece,
            move_location,
            current_board.current_player.other
        )
        # If the pawn is dropping to cause checkmate, not legal
        if is_checking:
            if mate_check(
                    current_board, {move_location},
                    act_full=move_location,
                    piece_pretend=piece,
                    king_color=current_board.other_player,
            ):
                return False
    # If any of the checking spaces can check the king, then the
    # drop is invalid
    for space in checking_spaces:
        if is_movable(
            current_board,
            (space, current_board.king_loc(piece.color)),
            act_full={move_location}
        ):
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
    king_location = current_board.king_loc(king_color)
    places_attacking = set()
    # If the piece can attack the king, it's check.
    # Otherwise, no other pieces have had a path to the king
    # magically opened up, so there's no check
    if is_movable(
            current_board,
            (new_location, king_location),
            act_full={new_location},
            piece_pretend=piece_to_drop,
    ):
        places_attacking.add(new_location)
    return places_attacking
