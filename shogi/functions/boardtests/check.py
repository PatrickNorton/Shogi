from shogi import classes
from .move import movecheck2
from typing import List, Tuple

__all__ = [
    "checkcheck",
    "checkcheck2"
]


def checkcheck(
    theboard: classes.Board,
    coords: Tuple[classes.Coord, classes.Coord],
    color: classes.Color,
    earlybreak: bool = False
) -> Tuple[bool, classes.Coord, List[classes.Coord]]:
    """Find if king is in check.

    Arguments:
        theboard {Board} -- current game board
        coords {tuple[Coord]} -- last move (from, to)
        color {Color} -- color of king to test

    Keyword Arguments:
        earlybreak {bool} -- break after first or second check
            (default: {False})

    Returns:
        bool -- if king is in check
        Coord -- location of king
        list[Coord] -- list of coords attacking king
    """

    oldloc, newloc = coords
    check: bool = False
    checklist: List[classes.Coord] = []
    toget: classes.Piece = classes.Piece('k', color)
    kingpos: classes.Coord = theboard.getpiece(toget)
    try:
        movecheck2(theboard, (newloc, kingpos))
    except classes.IllegalMove:
        check, checklist = checkcheck2(
            theboard,
            (oldloc, kingpos),
            checklist,
            earlybreak)
    else:
        if earlybreak:
            checklist.append(newloc)
            return True, kingpos, checklist
        else:
            checklist.append(newloc)
            check, checklist = checkcheck2(
                theboard,
                (oldloc, kingpos),
                checklist)
            return True, kingpos, checklist
    return check, kingpos, checklist


def checkcheck2(
    theboard: classes.Board,
    coords: Tuple[classes.Coord, classes.Coord],
    checklist: List[classes.Coord],
    earlybreak: bool = False
):
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
    relcoord: classes.Coord = kingpos-oldloc
    mvmt: classes.Coord = abs(relcoord)
    if mvmt.x != mvmt.y and min(mvmt):
        return False, checklist
    toking = classes.Direction(relcoord)
    doa = classes.Row(oldloc, toking)
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
