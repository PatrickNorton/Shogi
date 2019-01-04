from shogi import classes
from shogi.functions import boardtests
from typing import List

__all__ = [
    "testspcs"
]


def testspcs(
    theboard: classes.Board,
    pieceloc: classes.Coord,
    spacelist: List[classes.Coord]
):
    """Test which spaces in a list are valid moves.

    Arguments:
        theboard {Board} -- current state of the board
        pieceloc {Coord} -- location of piece to be moved
        spacelist {list[Coord]} -- list of coords to check

    Returns:
        list -- list of valid spaces
    """

    toreturn = []
    for relloc in spacelist:
        try:
            absloc = pieceloc+relloc
            boardtests.move_check_2(theboard, (pieceloc, absloc))
        except (TypeError, ValueError, classes.IllegalMove):
            continue
        else:
            toreturn.append(absloc)
    return toreturn
