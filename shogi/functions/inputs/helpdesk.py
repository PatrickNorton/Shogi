import json
from .movelistfn import movelistfn
from .helpmenu import helpmenu
from .filedisp import filedisp
from shogi import classes
from .inputfns import getinput
from .toquit import toquit
from .privates import _openhelp, _opendata

__all__ = [
    "helpdesk",
    "ltrtoname"
]

def helpdesk(input_gen, window, theboard, filenm=None):
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
    with _opendata('names.json') as f:
        namedict = json.load(f)
    if filenm.lower() in namedict:
        if filenm.islower():
            filenm = namedict[filenm]
        elif filenm.isupper():
            filenm = '+'+namedict[filenm.lower()]
    return filenm
