from shogi import classes

__all__ = [
    "inputpiece"
]

def inputpiece(theboard, pieceloc):
    try:
        pieceloc = classes.coord(pieceloc)
        return True
    except (ValueError, IndexError):
        raise classes.OtherInput(pieceloc)
