import json

from typing import Dict, List, TextIO, Union

__all__ = [
    "_InfoClass",
    "_open_data",
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
        moves_type = Dict[str, List[List[Union[int, List[str], bool]]]]

        with _open_data('moves.json') as f:
            self.move_info: moves_type = json.load(f)
        with _open_data('names.json') as f:
            self.name_info: Dict[str, str] = json.load(f)
        with _open_data('board.json') as f:
            self.board_info: Dict[str, List[str]] = json.load(f)
        with _open_data('other.json') as f:
            self.piece_info: Dict[str, dict] = json.load(f)
        with _open_data('errors.json') as f:
            self.error_info: List[str] = json.load(f)
        with _open_data('helpindex.json') as f:
            self.help_index: Dict[str, Union[str, dict]] = json.load(f)


def _open_data(file_name: str) -> TextIO:
    """Open data file.

    :param file_name: name of file to be opened

    :return: opened file
    """
    # import os
    # cwd = os.path.dirname(__file__)
    # file_path = os.path.join(cwd, f'../datafiles/{file_name}')
    # return open(file_path)
    import pathlib
    cwd = pathlib.Path(__file__).resolve().parent
    file_path = pathlib.Path(cwd, "..", "datafiles", file_name)
    return open(file_path)
