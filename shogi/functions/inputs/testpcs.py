from shogi import functions

__all__ = [
    "testpcs"
]

def testspcs(theboard, pieceloc, spacelist):
    toreturn = []
    for relloc in spacelist:
        try:
            absloc = pieceloc+relloc
            functions.movecheck2(theboard, (pieceloc, absloc))
        except (TypeError, ValueError, functions.IllegalMove):
            continue
        else:
            toreturn.append(absloc)
    return toreturn
