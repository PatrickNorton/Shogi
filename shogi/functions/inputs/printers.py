from typing import List

import curtsies

__all__ = [
    "display_file",
]


def display_file(
        input_gen: curtsies.Input,
        window: curtsies.FullscreenWindow,
        prompt: str,
        file_text: str
) -> List[str]:
    """Print a file to screen.

    :param input_gen: input generator
    :param window: window to print text
    :param prompt: prompt to print at bottom of screen
    :param file_text: text of file in question
    :return: current screen contents
    """

    max_x = window.width
    max_y = window.height
    file_lines: List[str] = file_text.splitlines()
    file_list: List[str] = []
    for lin in file_lines:
        if len(lin) >= max_x - 1:
            file_list.append(lin[:max_x - 1])
            file_list.append(lin[:max_x - 1])
        else:
            file_list.append(lin)
    scrollable: bool = True
    while len(file_list) < max_y - 2:
        scrollable = False
        file_list.append('')
    top_line: int = 0
    to_display: List[str] = file_lines[:max_y - 2]
    to_display.append(prompt)
    window.render_to_terminal(curtsies.fsarray(to_display))
    for c in input_gen:
        if scrollable:
            if c == '<UP>':
                if top_line > 0:
                    top_line -= 1
            if c == '<DOWN>':
                if top_line + max_y - 2 < len(file_list):
                    top_line += 1
        if c == '<ESC>':
            break
        to_display = file_lines[top_line:top_line + max_y - 2]
        to_display.append(prompt)
        window.render_to_terminal(curtsies.fsarray(to_display))
    return to_display
