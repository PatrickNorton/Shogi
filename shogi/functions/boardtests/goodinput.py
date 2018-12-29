from shogi import classes

__all__ = [
    "inputpiece"
]


def inputpiece(
    theboard: classes.Board,
    strloc: str
) -> bool:
    """Test if input is a valid location/

    Arguments:
        theboard {Board} -- current board state
        pieceloc {str} -- inputted string

    Raises:
        classes.OtherInput -- if input is not a valid location

    Returns:
        bool -- is input valid
    """

    try:
        pieceloc = classes.Coord(strloc)
        return True
    except (ValueError, IndexError):
        raise classes.OtherInput(pieceloc)
