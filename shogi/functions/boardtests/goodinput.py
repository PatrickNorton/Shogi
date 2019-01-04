from shogi import classes

__all__ = [
    "input_piece"
]


def input_piece(entered_text: str) -> classes.Coord:
    """Test if input is a valid location.

    :param entered_text: inputted string
    :raises classes.OtherInput: if non-coordinate input entered
    :return: coordinate entered
    """

    try:
        piece_location: classes.Coord = classes.Coord(entered_text)
        return piece_location
    except (ValueError, IndexError):
        raise classes.OtherInput(entered_text)
