from shogi import classes
from .piece import inputpiece

__all__ = [
    "piececheck"
]

def piececheck(theboard, pieceloc):
    validpiece = inputpiece(theboard, pieceloc)
    if not validpiece:
        raise classes.IllegalMove(11)
    pieceloc = classes.coord(pieceloc)
    if theboard[pieceloc].COLOR != theboard.currplyr:
        raise classes.IllegalMove(5)
    return pieceloc
