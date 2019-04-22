from shogi import classes
from .drop import is_legal_drop
from .fullmove import check_move

__all__ = [
    "undo_move",
]

# TODO: More descriptive ValueErrors


def undo_move(
        current_board: classes.Board,
        move: classes.Move
):
    """Undo given move.

    :param current_board: current board state
    :param move: move to undo
    """
    if move.is_drop:
        # If the move is a drop, un-drop it, and then test if it is a
        # legal drop to be made. If it isn't, put it back and raise an
        # error
        current_board.un_drop(move.end)
        if not is_legal_drop(
            current_board,
            move.piece,
            move.end
        ):
            current_board.put_in_play(move.piece, move.end)
            raise ValueError
    else:
        # If the move is not a drop, but a move, move it back to
        # whence it came, and then test to see if the reverse was a
        # legal move. If it wasn't, put it back and raise an error
        if current_board[move.start]:
            raise ValueError
        current_board.move(move.end, move.start)
        # If the move ended in promotion, un-promote the piece
        # If the move was a capture, put the captured piece back on
        # the board
        if move.is_capture:
            current_board.put_in_play(move.captured_piece, move.end)
        can_move = check_move(current_board, (move.start, move.end))
        if not can_move:
            current_board.move(move.start, move.end)
            raise ValueError
