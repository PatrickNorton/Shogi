from itertools import product
from shogi import classes
from .inputpiece import inputpiece

__all__ = [
    "movecheck",
    "movecheck2",
    "obscheck",
    "kingcheck"
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


def kingcheck(theboard, coords):
    oldloc, newloc = coords
    rowlist = (classes.direction(x) for x in range(8))
    for x, dist in product(rowlist, range(9)):
        dist = classes.coord(dist)
        try:
            loctotest = newloc+x*dist
            if theboard[loctotest].COLOR == theboard[oldloc].COLOR:
                raise classes.IllegalMove(4)
            movecheck2(theboard, (loctotest, newloc))
        except (ValueError, IndexError):
            continue
        except classes.IllegalMove as e:
            if str(e) == '2':
                break
            else:
                continue
        else:
            raise classes.IllegalMove(6)
    for delx, dely in product((-1, 1), (-1, 1)):
        relcoord = classes.coord((delx, 2*dely))
        try:
            abscoord = newloc+relcoord
            movecheck2(theboard, (abscoord, newloc))
        except (ValueError, IndexError):
            continue
        except classes.IllegalMove:
            continue
        else:
            raise classes.IllegalMove(6)
