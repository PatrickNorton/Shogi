import curtsies

__all__ = [
    "getinput",
    "yninput"
]

def getinput(input_gen, window, todisp):
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
    window.render_to_terminal(todisp)
    for c in input_gen:
        if c == 'y':
            return True
        if c == 'n':
            return False
        window.render_to_terminal(todisp)
