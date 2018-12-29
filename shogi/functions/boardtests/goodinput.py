from shogi import classes

__all__ = [
    "inputpiece"
]


def inputpiece(theboard, pieceloc):
    """Test if input is a valid location/

    Arguments:
        theboard {board} -- current board state
        pieceloc {str} -- inputted string

    Raises:
        classes.OtherInput -- if input is not a valid location

    Returns:
        bool -- is input valid
    """

    try:
        pieceloc = classes.Coord(pieceloc)
        return True
    except (ValueError, IndexError):
        raise classes.OtherInput(pieceloc)
