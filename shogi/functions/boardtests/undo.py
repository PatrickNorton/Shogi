from shogi import classes
from .drop import is_legal_drop
from .fullmove import check_move

__all__ = [
    "undo_move",
]

# TODO: More descriptive ValueErrors


def undo_move(
        current_board: classes.Board,
        move: 'classes.Move'
):
    """Undo given move.

    :param current_board: current board state
    :param move: move to undo
    """
    if move.is_drop:
        current_board.un_drop(move.end)
        can_drop = is_legal_drop(
            current_board,
            move.piece,
            move.end
        )
        if not can_drop:
            current_board.put_in_play(move.piece, move.end)
            raise ValueError
    else:
        if current_board[move.start]:
            raise ValueError
        current_board.move(move.end, move.start)
        if move.is_capture:
            current_board.put_in_play(move.captured_piece, move.end)
        can_drop = check_move(current_board, (move.start, move.end))
        if not can_drop:
            current_board.move(move.start, move.end)
            raise ValueError
