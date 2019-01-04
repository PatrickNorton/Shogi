from itertools import product
from shogi import classes
from .move import movecheck2
from typing import List

__all__ = [
    "matecheck"
]


def matecheck(
    theboard: classes.Board,
    kingpos: classes.Coord,
    checklist: List[classes.Coord]
) -> bool:
    """Test if king is in checkmate.

    Arguments:
        theboard {Board} -- current board position
        kingpos {Coord} -- location of king
        checklist {list[Coord]} -- list of pieces checking king

    Returns:
        bool -- if king is in checkmate
    """

    kingmovepos = (classes.Direction(x) for x in range(8))
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
    checkloc = checklist[0]
    relpos = kingpos-checkloc
    haspieces = theboard.CAPTURED[int(theboard.currplyr)]
    notknight = str(theboard[checkloc].PTYPE) != 'n'
    hasspace = not all(x in (-1, 0, 1) for x in relpos)
    if haspieces and notknight and hasspace:
        return False
    for loc in theboard.enemypcs:
        try:
            movecheck2(theboard, (loc, checkloc))
        except classes.IllegalMove:
            continue
        return False
    move = kingpos-checkloc
    movedir = classes.Direction(move)
    for pos, z in product(theboard.enemypcs, range(abs(max(move)))):
        newpos = checkloc*classes.Coord(movedir)*z
        try:
            movecheck2(theboard, (pos, newpos))
        except classes.IllegalMove:
            continue
        return False
    return True
