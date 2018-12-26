from itertools import product
from shogi import classes
from .movecheck import movecheck2

__all__ = [
    "kingcheck"
]

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
