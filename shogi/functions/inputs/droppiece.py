from shogi import classes
from shogi import functions
from .inputfns import getinput
from .otherconditions import otherconditions

__all__ = [
    "droppiece"
]

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
