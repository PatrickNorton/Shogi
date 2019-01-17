import curtsies

from typing import Dict, List

from shogi import classes
from shogi.functions import boardtests

from .inputfns import get_input

__all__ = [
    "setup_board"
]


def setup_board(
        input_gen: curtsies.Input,
        window: curtsies.FullscreenWindow
):
    """Set up an already-started board.

    :param input_gen: input generator
    :param window: window displayed
    :return: newly set-up board
    """

    piece_dict: Dict[classes.AbsoluteCoord, classes.Piece] = {}
    while True:
        to_display: List[str] = ['Choose location']
        inputted_text: str = get_input(input_gen, window, to_display)
        inputted_text = inputted_text.strip()
        if inputted_text == 'done':
            to_display.append('Board completed')
            window.render_to_terminal(curtsies.fsarray(to_display))
            break
        try:
            coordinate: classes.AbsoluteCoord = boardtests.input_piece(inputted_text)
        except classes.OtherInput:
            to_display.append("Invalid input")
            continue
        to_display.append('Choose piece and color ')
        piece_string: str = get_input(input_gen, window, to_display)
        try:
            piece_name: classes.Piece = classes.Piece(*piece_string)
        except (ValueError, IndexError):
            print('Invalid piece\n')
            continue
        piece_dict[coordinate] = piece_name
    to_return = classes.Board(piece_dict)
    return to_return
