from shogi import classes
from shogi import functions

__all__ = [
    "testspcs"
]

def testspcs(theboard, pieceloc, spacelist):
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
