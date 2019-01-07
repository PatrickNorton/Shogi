import curtsies
from shogi import classes
from shogi.functions import boardtests
from .help import help_desk
from .inputfns import get_input, binary_input
from typing import List

__all__ = [
    "other_conditions",
    "drop_piece",
    "may_quit"
]


def other_conditions(
    input_gen: curtsies.Input,
    window: curtsies.FullscreenWindow,
    to_display: List[str],
    current_board: classes.Board,
    entered_text: str
) -> bool:
    """Check if string is an action, then do the action.

    :param input_gen: input generator
    :param window: window to print text
    :param to_display: what's currently on screen
    :param current_board: current board setup
    :param entered_text: text inputted by user
    :raises classes.IllegalMove: restart move with current player
    :return: if a valid turn was held
    """

    if entered_text == 'drop':
        drop_piece(input_gen, window, to_display, current_board)
        return True
    if entered_text == 'quit':
        may_quit(input_gen, window, to_display)
        raise classes.IllegalMove(0)
    if entered_text == 'help':
        help_desk(input_gen, window, current_board)
        raise classes.IllegalMove(0)
    if entered_text[:4] == 'help':
        file_name: str = entered_text[4:]
        file_name = file_name.strip()
        help_desk(input_gen, window, current_board, file_name)
        raise classes.IllegalMove(0)
    return False


def drop_piece(
    input_gen: curtsies.Input,
    window: curtsies.FullscreenWindow,
    to_display: List[str],
    current_board: classes.Board
):
    """Prompt to add a piece to the board.

    :param input_gen: input generator
    :param window: window to print text
    :param to_display: list of what's currently on screen
    :param current_board: current state of board
    :raises classes.IllegalMove: attempted drop of un-captured piece
    :raises classes.IllegalMove: illegal drop attempted
    """

    if not current_board.captured[current_board.current_player]:
        raise classes.IllegalMove(7)
    to_display.append('Enter piece name to put in play')
    to_display.append('> ')
    moved = get_input(input_gen, window, to_display)
    if moved.startswith('k'):
        moved = 'n'
    to_display = to_display[:-2]
    try:
        to_drop = classes.Piece(moved[0], current_board.current_player)
    except ValueError:
        return
    if to_drop in current_board.captured[current_board.current_player]:
        to_display.append('Enter location to place piece')
        to_display.append(': ')
        entered_str: str = get_input(input_gen, window, to_display)
        try:
            move_to: classes.AbsoluteCoord = boardtests.input_piece(entered_str)
        except classes.OtherInput:
            other_conditions(input_gen, window, to_display, current_board, entered_str)
        else:
            current_board.put_in_play(to_drop, move_to)


def may_quit(
    input_gen: curtsies.Input,
    window: curtsies.FullscreenWindow,
    to_display: List[str]
):
    """Check if player really wants to quit.

    :param input_gen: input generator
    :param window: window to print text
    :param to_display: list of stuff on screen
    :raises classes.PlayerExit: player wishes to exit
    """

    while True:
        to_display.append('You are about to quit the game.')
        to_display.append('Are you sure you want to quit?')
        to_quit: bool = binary_input(input_gen, window, to_display)
        if to_quit:
            raise classes.PlayerExit
