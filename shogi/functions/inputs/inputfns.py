import curtsies
from curtsies import events
from typing import List

__all__ = [
    "get_input",
    "binary_input"
]


def get_input(
    input_gen: curtsies.Input,
    window: curtsies.FullscreenWindow,
    to_print: List[str]
) -> str:
    """Get player input and return a string.

    :param input_gen: input generator
    :param window: window to print text
    :param to_print: prompt to print before input
    :return: text entered by user
    """

    to_return = ''
    window.render_to_terminal(curtsies.fsarray(to_print))
    escape_code = 0
    for c in input_gen:
        if escape_code:
            escape_code -= 1
            continue
        if isinstance(c, events.PasteEvent):
            continue
        if c == '<Ctrl-j>':
            break
        elif c == '<BACKSPACE>':
            to_print[-1] = to_print[-1][:-1]
            to_return = to_return[:-1]
        elif c == '<SPACE>':
            to_print[-1] += ' '
            to_return += ' '
        elif c.startswith('<'):
            continue
        elif len(c) > 1:
            escape_code = 3
            continue
        else:
            to_print[-1] += c
            to_return += c
        window.render_to_terminal(curtsies.fsarray(to_print))
    return to_return


def binary_input(
    input_gen: curtsies.Input,
    window: curtsies.FullscreenWindow,
    to_print: List[str]
) -> bool:
    """Get binary (y/n) input from user.

    :param input_gen: generate input
    :param window: window to print text
    :param to_print: prompt to print before input
    :return: y/n entered by user
    """

    window.render_to_terminal(curtsies.fsarray(to_print))
    for c in input_gen:
        if c == 'y':
            return True
        if c == 'n':
            return False
        window.render_to_terminal(curtsies.fsarray(to_print))
    return False
