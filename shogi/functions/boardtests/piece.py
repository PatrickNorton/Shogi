from shogi import classes
from .goodinput import inputpiece

__all__ = [
    "piececheck"
]


def piececheck(theboard, pieceloc):
    """Check if inputted piece is valid.

    Arguments:
        theboard {Board} -- current board state
        pieceloc {str} -- inputted string of location

    Raises:
        classes.IllegalMove -- invalid entry of piece
        classes.IllegalMove -- entry of location without their piece

    Returns:
        Coord -- location inputted
    """

    validpiece = inputpiece(theboard, pieceloc)
    if not validpiece:
        raise classes.IllegalMove(11)
    pieceloc = classes.Coord(pieceloc)
    if theboard[pieceloc].COLOR != theboard.currplyr:
        raise classes.IllegalMove(5)
    return pieceloc
