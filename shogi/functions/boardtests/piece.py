from shogi import classes
from .goodinput import inputpiece

__all__ = [
    "piececheck"
]


def piececheck(theboard, pieceloc):
    """Check if inputted piece is valid.

    Arguments:
        theboard {board} -- current board state
        pieceloc {str} -- inputted string of location

    Raises:
        classes.IllegalMove -- invalid entry of piece
        classes.IllegalMove -- entry of location without their piece

    Returns:
        coord -- location inputted
    """

    validpiece = inputpiece(theboard, pieceloc)
    if not validpiece:
        raise classes.IllegalMove(11)
    pieceloc = classes.coord(pieceloc)
    if theboard[pieceloc].COLOR != theboard.currplyr:
        raise classes.IllegalMove(5)
    return pieceloc
