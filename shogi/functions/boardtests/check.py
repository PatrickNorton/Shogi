from shogi import classes
from .move import movecheck2

__all__ = [
    "checkcheck",
    "checkcheck2"
]


def checkcheck(theboard, coords, color, earlybreak=False):
    """Find if king is in check.

    Arguments:
        theboard {Board} -- current game board
        coords {tuple[Coord]} -- last move (from, to)
        color {color} -- color of king to test

    Keyword Arguments:
        earlybreak {bool} -- break after first or second check
            (default: {False})

    Returns:
        bool -- if king is in check
        Coord -- location of king
        list[Coord] -- list of coords attacking king
    """

    oldloc, newloc = coords
    check, checklist = False, []
    toget = classes.piece('k', color)
    kingpos = theboard.getpiece(toget)
    try:
        movecheck2(theboard, (newloc, kingpos))
    except classes.IllegalMove:
        tocc2 = ((oldloc, kingpos), [], earlybreak)
        check, checklist = checkcheck2(theboard, *tocc2)
    else:
        if earlybreak:
            checklist.append(newloc)
            return True, kingpos, checklist
        else:
            checklist.append(newloc)
            tocc2 = ((oldloc, kingpos), checklist, earlybreak)
            check, checklist = checkcheck2(theboard, *tocc2)
            return True, kingpos, checklist
    return check, kingpos, checklist


def checkcheck2(theboard, coords, checklist, earlybreak=False):
    """Test if non-moved pieces can check king.

    Arguments:
        theboard {Board} -- current board
        coords {tuple[Coord]} -- last move(from, to)
        checklist {list[Coord]} -- list of pieces currently checking king

    Keyword Arguments:
        earlybreak {bool} -- break after first check (default: {False})

    Returns:
        bool -- king in check
        list[Coord] -- pieces checking king
    """

    oldloc, kingpos = coords
    relcoord = kingpos-oldloc
    mvmt = abs(relcoord)
    if mvmt.x != mvmt.y and min(mvmt):
        return False, checklist
    toking = classes.Direction(relcoord)
    doa = classes.row(oldloc, toking)
    currpieces = theboard.playerpcs(theboard[kingpos].COLOR.other)
    pieces = (x for x in doa if x in currpieces)
    for x in pieces:
        try:
            movecheck2(theboard, (x, kingpos))
        except classes.IllegalMove:
            continue
        else:
            checklist.append(x)
            if earlybreak or len(checklist) > 1:
                return True, checklist
            else:
                continue
    return False, checklist
