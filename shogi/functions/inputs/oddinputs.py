from shogi import classes
from shogi import functions
from .help import helpdesk
from .inputfns import getinput

__all__ = [
    "otherconditions",
    "droppiece",
    "toquit"
]

def otherconditions(input_gen, window, todisp, theboard, var):
    if var == 'drop':
        droppiece(input_gen, window, todisp, theboard)
        return True
    if var == 'quit':
        toquit(input_gen, window, todisp)
        raise classes.IllegalMove(0)
    if var == 'help':
        helpdesk(input_gen, window, theboard)
        raise classes.IllegalMove(0)
    if var[:4] == 'help':
        filenm = var[4:]
        filenm = filenm.strip()
        helpdesk(input_gen, window, theboard, filenm)
        raise classes.IllegalMove(0)


def droppiece(input_gen, window, todisp, theboard):
    if not theboard.CAPTURED[theboard.currplyr]:
        raise classes.IllegalMove(7)
    todisp.append('Enter piece name to put in play')
    todisp.append('> ')
    if moved.startswith('k'):
        moved = 'n'
    try:
        todisp = todisp[:-2]
        thepiece = classes.piece(moved[0], theboard.currplyr)
        if thepiece in theboard.CAPTURED[theboard.currplyr]:
            todisp.append('Enter location to place piece')
            todisp.append(': ')
            moveto = getinput(input_gen, window, todisp)
            if functions.inputpiece(theboard, moveto):
                moveto = classes.coord(moveto)
                theboard.putinplay(thepiece, moveto)
        else:
            raise classes.IllegalMove(10)
    except ValueError:
        pass
    except functions.OtherInput:
        otherconditions(input_gen, window, todisp, theboard, moveto)


def toquit(input_gen, window, todisp):
    while True:
        todisp.append('You are about to quit the game of Shogi')
        todisp.append('Are you sure you want to quit?')
        window.render_to_terminal(todisp)
        for c in input_gen:
            if c == 'y':
                toquit = True
                break
            elif c == 'n':
                toquit = False
                break
        if toquit:
            raise functions.PlayerExit
        else:
            break
