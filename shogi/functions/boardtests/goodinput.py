from shogi import classes, Coord

__all__ = [
    "input_piece"
]


def input_piece(entered_text: str) -> classes.Coord:
    """Test if input is a valid location/

    Arguments:
        entered_text {str} -- inputted string

    Raises:
        classes.OtherInput -- if input is not a valid location

    Returns:
        bool -- is input valid
    """

    try:
        piece_location: classes.Coord = classes.Coord(entered_text)
        return piece_location
    except (ValueError, IndexError):
        raise classes.OtherInput(entered_text)
