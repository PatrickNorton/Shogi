import json
import curtsies
from .printers import display_file
from shogi import classes
from .inputfns import get_input
from .quitting import toquit
from .privates import _open_help, _open_data
from .findmoves import test_spaces
from typing import List, Dict, Union

__all__ = [
    "help_desk",
    "letter_to_name",
    "help_menu",
    "list_moves"
]


def help_desk(
        input_gen: curtsies.Input,
        window: curtsies.FullscreenWindow,
        current_board: classes.Board,
        file_name: str = ''
):
    """Run help functions.

    :param input_gen: input generator
    :param window: window to display text
    :param current_board: current state of board
    :param file_name: name of file, if provided
    :raises classes.IllegalMove: continue with turn
    """

    with _open_help('main.txt') as f:
        main_text = f.read()
    if file_name:
        if file_name == 'moves':
            list_moves(input_gen, window, current_board)
            return
        if file_name == 'menu':
            file_name = help_menu(input_gen, window)
            file_name = file_name[:-4]
        file_name = letter_to_name(file_name)
        try:
            with _open_help(f"{file_name}.txt") as f:
                file_text = f.read()
            prompt = 'Press Esc to return to game'
            display_file(input_gen, window, prompt, file_text)
            raise classes.IllegalMove(0)
        except FileNotFoundError:
            invalid_prompt = (
                'Invalid help command. Type "help" for command list.'
            )
            print(invalid_prompt)
        return
    prompt = 'Press Esc to activate help menu'
    to_display = display_file(input_gen, window, prompt, main_text)
    while True:
        to_display = to_display[:-1]
        to_display.append('help: ')
        file_name = get_input(input_gen, window, to_display)
        file_name = file_name.strip()
        file_lower = file_name.lower()
        if file_lower == 'exit':
            break
        elif file_lower == 'quit':
            toquit(input_gen, window, to_display)
        elif file_lower == 'moves':
            list_moves(input_gen, window, current_board)
        else:
            if file_lower == 'menu':
                file_name = help_menu(input_gen, window)
                file_name = file_name[:-4]
            file_name = letter_to_name(file_name)
            file_name = file_name.lower()
            try:
                with _open_data(file_name) as f:
                    main_text = f.read()
                prompt = 'Press Esc to activate help menu'
                to_display = display_file(input_gen, window, prompt, main_text)
            except FileNotFoundError:
                print('Invalid help command\n')
                with _open_help("helpcommands.txt") as f:
                    commands = f.read()
                print(commands)
    raise classes.IllegalMove(0)


def letter_to_name(file_name: str) -> str:
    """Turn single-letter inputs into a piece name.

    :param file_name: name inputted
    :return: full name of piece
    """

    with _open_data('names.json') as f:
        name_dict: Dict[str, str] = json.load(f)
    if file_name.lower() in name_dict:
        if file_name.islower():
            file_name = name_dict[file_name]
        elif file_name.isupper():
            file_name = '+' + name_dict[file_name.lower()]
    return file_name


def help_menu(
        input_gen: curtsies.Input,
        window: curtsies.FullscreenWindow
) -> str:
    """Function for interactive help menu.

    :param input_gen: input generator
    :param window: window on which to print
    :return: path of file to open
    """

    help_index: Dict[str, Union[str, dict]] = classes.info.HELPINDEX
    while True:
        to_display: List[str] = list(help_index)
        to_display.extend(['', '', ''])
        to_display.append('menu: ')
        window.render_to_terminal(curtsies.fsarray(to_display))
        file_name = get_input(input_gen, window, to_display)
        try:
            file_int: int = int(file_name)
            file_name: str = to_display[file_int]
        except ValueError:
            pass
        file_path: Union[str, dict] = help_index[file_name]
        if isinstance(file_path, str):
            break
        elif isinstance(file_path, dict):
            help_index: List[str, Union[str, dict]] = file_path
    return file_path


def list_moves(
        input_gen: curtsies.Input,
        window: curtsies.FullscreenWindow,
        current_board: classes.Board
):
    """List all possible moves for a player.

    :param input_gen: input generator
    :param window: window on which to display text
    :param current_board: current board
    """

    moves = {}
    current_pieces = current_board.currpcs
    for location, piece in current_pieces.items():
        move_list = []
        direction_list = (classes.Direction(x) for x in range(8))
        for x in direction_list:
            to_list = piece.validspaces(x)
            to_list = test_spaces(current_board, location, to_list)
            move_list += to_list
        moves[location] = move_list
    file_string = ''
    for location, piece in current_pieces.items():
        file_string += f"{piece !r} at {location}:\n"
        to_print = (str(x) for x in moves[location])
        file_string += f"    {', '.join(to_print)}\n"
    file_string = file_string.strip()
    prompt = "Press Esc to return to game"
    display_file(input_gen, window, prompt, file_string)
