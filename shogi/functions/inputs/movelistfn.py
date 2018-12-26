from shogi import classes
from .testpcs import testspcs
from .filedisp import filedisp

__all__ = [
    "movelistfn"
]

def movelistfn(input_gen, window, theboard):
    movedict = {}
    currpieces = theboard.currpcs()
    for loc, apiece in currpieces.items():
        movelst = []
        dirlist = (classes.direction(x) for x in range(8))
        for x in dirlist:
            tolst = apiece.validspaces(x)
            tolst = testspcs(theboard, loc, tolst)
            movelst += tolst
        movedict[loc] = movelst
    filestr = ''
    for loc, piece in currpieces.items():
        filestr += f"{repr(piece)} at {loc}:\n"
        toprint = (str(x) for x in movedict[loc])
        filestr += f"    {', '.join(toprint)}\n"
    filestr = filestr.strip()
    prompt = "Press Esc to return to game"
    filedisp(input_gen, window, prompt, filestr)
