from shogi import classes
from .kingcheck import kingcheck
from .inputpiece import inputpiece

__all__ = [
    "movecheck",
    "movecheck2",
    "obscheck"
]

def movecheck(theboard, current, moveloc):
    validpiece = inputpiece(theboard, moveloc)
    if not validpiece:
        raise classes.IllegalMove(11)
    moveloc = classes.coord(moveloc)
    return (current, moveloc)


def movecheck2(theboard, coords):
    current, new = coords
    piece = theboard[current]
    move = new-current
    movedir = classes.direction(move)
    magicvar = piece.MOVES[movedir]
    if movedir == classes.direction(8):
        raise classes.IllegalMove(3)
    elif not piece.canmove(move):
        raise classes.IllegalMove(1)
    elif theboard[new].COLOR == theboard[current].COLOR:
        raise classes.IllegalMove(4)
    elif magicvar == 'T':
        pass
    elif str(piece.PTYPE) == 'k':
        kingcheck(theboard, (current, new))
    else:
        obscheck(theboard, current, move)


def obscheck(theboard, current, move):
    movedir = classes.direction(move)
    for x in range(1, max(abs(move))):
        relcoord = [x*k for k in movedir]
        testpos = current+classes.coord(relcoord)
        if theboard[testpos]:
            raise classes.IllegalMove(2)
