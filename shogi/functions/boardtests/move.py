from itertools import product
from shogi import classes
from .goodinput import inputpiece

__all__ = [
    "movecheck",
    "movecheck2",
    "obscheck",
    "kingcheck"
]


def movecheck(theboard, current, moveloc):
    """Check if inputted piece is a valid piece

    TODO: deprecate this in favor of direct inputpiece call

    Arguments:
        theboard {Board} -- current board state
        current {Coord} -- position of piece to be moved
        moveloc {str} -- input of piece to be moved

    Raises:
        classes.IllegalMove -- invalid entry

    Returns:
        tuple[Coord] -- coords of movement
    """

    validpiece = inputpiece(theboard, moveloc)
    if not validpiece:
        raise classes.IllegalMove(11)
    moveloc = classes.Coord(moveloc)
    return (current, moveloc)


def movecheck2(theboard, coords):
    """Check if piece can be moved between locations.

    Arguments:
        theboard {Board} -- current board state
        coords {tuple[Coord]} -- current and new locations of piece

    Raises:
        classes.IllegalMove -- attempted zero-move of piece
        classes.IllegalMove -- move to illegal location
        classes.IllegalMove -- capture of own piece
    """

    current, new = coords
    piece = theboard[current]
    move = new-current
    movedir = classes.Direction(move)
    magicvar = piece.MOVES[movedir]
    if movedir == classes.Direction(8):
        raise classes.IllegalMove(3)
    elif not piece.canmove(move):
        raise classes.IllegalMove(1)
    elif theboard[new].samecolor(theboard[current]):
        raise classes.IllegalMove(4)
    elif magicvar == 'T':
        pass
    elif piece.istype('k'):
        kingcheck(theboard, (current, new))
    else:
        obscheck(theboard, current, move)


def obscheck(theboard, current, move):
    """Check if piece is obstructing move.

    Arguments:
        theboard {Board} -- current board state
        current {Coord} -- current piece location
        move {Coord} -- location to move piece

    Raises:
        classes.IllegalMove -- obstruction found
    """

    movedir = classes.Direction(move)
    for x in range(1, max(abs(move))):
        relcoord = [x*k for k in movedir]
        testpos = current+classes.Coord(relcoord)
        if theboard[testpos]:
            raise classes.IllegalMove(2)


def kingcheck(theboard, coords):
    """Check if king is moving into check.

    Arguments:
        theboard {Board} -- current board state
        coords {tuple[Coord]} -- current and new piece location

    Raises:
        classes.IllegalMove -- attempted capture of own piece
        classes.IllegalMove -- attempted move into check
        classes.IllegalMove -- attempted move into check
    """

    oldloc, newloc = coords
    rowlist = (classes.Direction(x) for x in range(8))
    for x, dist in product(rowlist, range(9)):
        dist = classes.Coord(dist)
        try:
            loctotest = newloc+x*dist
            if theboard[loctotest].samecolor(theboard[oldloc]):
                raise classes.IllegalMove(4)
            movecheck2(theboard, (loctotest, newloc))
        except (ValueError, IndexError):
            continue
        except classes.IllegalMove as e:
            if int(e) == '2':
                break
            else:
                continue
        else:
            raise classes.IllegalMove(6)
    for delx, dely in product((-1, 1), (-1, 1)):
        relcoord = classes.Coord((delx, 2*dely))
        try:
            abscoord = newloc+relcoord
            movecheck2(theboard, (abscoord, newloc))
        except (ValueError, IndexError):
            continue
        except classes.IllegalMove:
            continue
        else:
            raise classes.IllegalMove(6)
