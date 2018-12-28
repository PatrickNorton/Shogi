import curtsies

__all__ = [
    "getinput",
    "yninput"
]


def getinput(input_gen, window, todisp):
    """Get player input and return a string

    Arguments:
        input_gen {curtsies.Input} -- generates input
        window {curtsies.FullScreenWindow} -- window to print text
        todisp {str} -- prompt to print before input

    Returns:
        str -- text entered by user
    """

    toreturn = ''
    window.render_to_terminal(todisp)
    esccode = 0
    for c in input_gen:
        if esccode:
            esccode -= 1
            continue
        if isinstance(c, curtsies.events.PasteEvent):
            continue
        if c == '<Ctrl-j>':
            break
        elif c == '<BACKSPACE>':
            todisp[-1] = todisp[-1][:-1]
            toreturn = toreturn[:-1]
        elif c == '<SPACE>':
            todisp[-1] += ' '
            toreturn += ' '
        elif c.startswith('<'):
            continue
        elif len(c) > 1:
            esccode = 3
            continue
        else:
            todisp[-1] += c
            toreturn += c
        window.render_to_terminal(todisp)
    return toreturn


def yninput(input_gen, window, todisp):
    """Get binary (y/n) input from user.

    Arguments:
        input_gen {curtsies.Input} -- generate input
        window {curtsies.FullScreenWindow} -- window to print text
        todisp {str} -- prompt to print before input

    Returns:
        bool -- y/n entered by user
    """

    window.render_to_terminal(todisp)
    for c in input_gen:
        if c == 'y':
            return True
        if c == 'n':
            return False
        window.render_to_terminal(todisp)
