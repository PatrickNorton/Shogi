from shogi import classes
from .droppiece import droppiece
from .toquit import toquit
from .helpdesk import helpdesk

__all__ = [
    "otherconditions"
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
