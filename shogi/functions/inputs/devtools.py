from shogi import classes
from .inputfns import getinput
from shogi import functions
from .oddinputs import otherconditions

__all__ = [
    "setpos"
]


def setpos(input_gen, window):
    """Set up a board in mid-game.

    Arguments:
        input_gen {curtsies.Input} -- input generator
        window {curtsies.FullScreenWindow} -- window displayed

    Returns:
        Board -- the newly set-up board
    """

    theboard = classes.Board()
    todict = {}
    while True:
        todisp = []
        todisp.append('Choose location')
        loc = getinput(input_gen, window, todisp)
        loc = loc.strip()
        if loc == 'done':
            todisp.append('Board completed')
            window.render_to_terminal(todisp)
            break
        try:
            valid = functions.inputpiece(input_gen, window)
        except functions.OtherInput:
            otherconditions(input_gen, window, todisp, theboard, loc)
        if not valid:
            print('Invalid location')
            continue
        loc = classes.Coord(loc)
        todisp.append('Choose piece and color ')
        pcstr = getinput(input_gen, window, todisp)
        try:
            piecenm = classes.Piece(*pcstr)
        except (ValueError, IndexError):
            print('Invalid piece\n')
            continue
        todict[loc] = piecenm
    toreturn = classes.Board(todict)
    return toreturn
