import json
from .printers import filedisp
from shogi import classes
from .inputfns import getinput
from .quitting import toquit
from .privates import _openhelp, _opendata
from .findmoves import testspcs

__all__ = [
    "helpdesk",
    "ltrtoname",
    "helpmenu",
    "movelistfn"
]


def helpdesk(input_gen, window, theboard, filenm=None):
    """Run help functions.

    Arguments:
        input_gen {curtsies.Input} -- input generator
        window {curtsies.FullScreenWindow} -- window to display text
        theboard {Board} -- current state of board

    Keyword Arguments:
        filenm {str} -- name of file, if provided (default: {None})

    Raises:
        classes.IllegalMove -- return to game and continue with next turn
    """

    todisp = []
    with open('shogihelp.txt') as helpf:
        filetxt = helpf.read()
    if filenm is not None:
        if filenm == 'moves':
            movelistfn(input_gen, window, theboard)
            return
        if filenm == 'menu':
            filenm = helpmenu(input_gen, window, theboard)
            filenm = filenm[:-4]
        filenm = ltrtoname(filenm)
        try:
            with _openhelp(f"{filenm}.txt") as f:
                thefile = f.read()
            prompt = 'Press Esc to return to game'
            filedisp(input_gen, window, prompt, thefile)
            raise classes.IllegalMove(0)
        except FileNotFoundError as f:
            toout = 'Invalid help command. Type "help" for command list.'
            print(toout)
        return
    prompt = 'Press Esc to activate help menu'
    todisp = filedisp(input_gen, window, prompt, filetxt)
    while True:
        todisp = todisp[:-1]
        todisp.append('help: ')
        filenm = getinput(input_gen, window, todisp)
        filenm = filenm.strip()
        filelwr = filenm.lower()
        if filelwr == 'exit':
            break
        elif filelwr == 'quit':
            toquit(input_gen, window, todisp)
        elif filelwr == 'moves':
            movelistfn(input_gen, window, theboard)
        else:
            if filelwr == 'menu':
                filenm = helpmenu(input_gen, window, theboard)
                filenm = filenm[:-4]
            filenm = ltrtoname(filenm)
            filenm = filenm.lower()
            try:
                with _opendata(filenm) as f:
                    filetxt = f.read()
                prompt = 'Press Esc to activate help menu'
                todisp = filedisp(input_gen, window, prompt, filetxt)
            except FileNotFoundError:
                print('Invalid help command\n')
                with _openhelp("helpcommands.txt") as f:
                    commands = f.read()
                print(commands)
    raise classes.IllegalMove(0)


def ltrtoname(filenm):
    """Turn single-letter inputs into a piece name.

    Arguments:
        filenm {str} -- name inputted

    Returns:
        str -- full name of piece
    """

    with _opendata('names.json') as f:
        namedict = json.load(f)
    if filenm.lower() in namedict:
        if filenm.islower():
            filenm = namedict[filenm]
        elif filenm.isupper():
            filenm = '+'+namedict[filenm.lower()]
    return filenm


def helpmenu(input_gen, window, theboard):
    """Function for interactive help menu.

    Arguments:
        input_gen {curtsies.Input} -- Input generator
        window {curtsies.FullScreenWindow} -- window on which to print
        theboard {Board} -- current state of the board

    Returns:
        str -- path of file to open
    """

    index = classes.info.HELPINDEX
    while True:
        todisp = list(index)
        todisp.extend(['', '', ''])
        todisp.append('menu: ')
        window.render_to_terminal(todisp)
        filenm = getinput(input_gen, window, todisp)
        try:
            filenm = int(filenm)
            filenm = todisp.index(filenm)
        except ValueError:
            pass
        filepath = index[filenm]
        if isinstance(filepath, str):
            break
        elif isinstance(filepath, dict):
            index = filepath
    return filepath


def movelistfn(input_gen, window, theboard):
    """List all possible moves for a player.

    Arguments:
        input_gen {curtsies.Input} -- input generator
        window {curtsies.FullScreenWindow} -- window to display text
        theboard {Board} -- current gameplay board
    """

    movedict = {}
    currpieces = theboard.currpcs
    for loc, apiece in currpieces.items():
        movelst = []
        dirlist = (classes.Direction(x) for x in range(8))
        for x in dirlist:
            tolst = apiece.validspaces(x)
            tolst = testspcs(theboard, loc, tolst)
            movelst += tolst
        movedict[loc] = movelst
    filestr = ''
    for loc, piece in currpieces.items():
        filestr += f"{piece !r} at {loc}:\n"
        toprint = (str(x) for x in movedict[loc])
        filestr += f"    {', '.join(toprint)}\n"
    filestr = filestr.strip()
    prompt = "Press Esc to return to game"
    filedisp(input_gen, window, prompt, filestr)
