from itertools import product
from shogi import classes
from .move import movecheck2

__all__ = [
    "matecheck"
]

def matecheck(theboard, kingpos, checklist):
    kingmovepos = (classes.direction(x) for x in range(8))
    for kmpiter in kingmovepos:
        newpos = kmpiter+kingpos
        if tuple(newpos) in theboard.it():
            try:
                movecheck2(theboard, (kingpos, newpos))
            except classes.IllegalMove:
                continue
            else:
                return False
    if len(checklist) > 1:
        return True
    checklist = checklist[0]
    haspieces = theboard.CAPTURED[int(theboard.currplyr)]
    notknight = str(theboard[checklist].PTYPE) != 'n'
    hasspace = not all(x in (-1, 0, 1) for x in newpos)
    if haspieces and notknight and hasspace:
        return False
    for loc in theboard.enemypcs():
        try:
            movecheck2(theboard, (loc, checklist))
        except classes.IllegalMove:
            continue
        return False
    move = kingpos-checklist
    movedir = classes.direction(move)
    for pos, z in product(theboard.enemypcs(), range(abs(max(move)))):
        newpos = z*checklist*classes.coord(movedir)
        try:
            movecheck2(theboard, (pos, newpos))
        except classes.IllegalMove:
            continue
        return False
    return True
