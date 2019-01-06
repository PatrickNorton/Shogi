import json
from typing import Dict, List, Union, TextIO

__all__ = [
    "_InfoClass",
    "_opendata"
]


class _InfoClass:
    """The class that gets all the info from json files.

    :ivar move_info: moves.json
    :ivar name_info: names.json
    :ivar board_info: board.json
    :ivar piece_info: other.json
    :ivar error_info: errors.json
    :ivar help_index: helpindex.json
    """

    def __init__(self):
        """Initialise instance of Piece."""

        with _opendata('moves.json') as f:
            self.move_info: Dict[str, List[str]] = json.load(f)
        with _opendata('names.json') as f:
            self.name_info: Dict[str, str] = json.load(f)
        with _opendata('board.json') as f:
            self.board_info: Dict[str, List[str]] = json.load(f)
        with _opendata('other.json') as f:
            self.piece_info: Dict[str, dict] = json.load(f)
        with _opendata('errors.json') as f:
            self.error_info: List[str] = json.load(f)
        with _opendata('helpindex.json') as f:
            self.help_index: Dict[str, Union[str, dict]] = json.load(f)


def _opendata(filenm: str) -> TextIO:
    """Open data file.

    Arguments:
        filenm {str} -- name of file to be opened

    Returns:
        file -- opened file
    """

    import os
    cwd = os.path.dirname(__file__)
    file_path = os.path.join(cwd, f'../datafiles/{filenm}')
    return open(file_path)
