from shogi import classes
from shogi import functions

__all__ = [
    "testspcs"
]


def testspcs(theboard, pieceloc, spacelist):
    """Test which spaces in a list are valid moves.

    Arguments:
        theboard {board} -- current state of the board
        pieceloc {coord} -- location of piece to be moved
        spacelist {list[coord]} -- list of coords to check

    Returns:
        list -- list of valid spaces
    """

    toreturn = []
    for relloc in spacelist:
        try:
            absloc = pieceloc+relloc
            functions.movecheck2(theboard, (pieceloc, absloc))
        except (TypeError, ValueError, classes.IllegalMove):
            continue
        else:
            toreturn.append(absloc)
    return toreturn
