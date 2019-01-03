import json
from typing import Dict, List, Union, TextIO

__all__ = [
    "_Infocls",
    "_opendata"
]


class _Infocls:
    """The class that gets all the info from json.

    Properties:
        MOVEDICT {dict} -- moves.json
        NAMEDICT {dict} -- names.json
        LS {dict} -- board.json
        PCINFO {dict} -- other.json
        ERRORS {list} -- errors.json
        HELPINDEX {dict} -- helpindex.json
    """

    def __init__(self):
        """Initialise instance of Piece."""

        with _opendata('moves.json') as f:
            self.MOVEDICT: Dict[str, List[str]] = json.load(f)
        with _opendata('names.json') as f:
            self.NAMEDICT: Dict[str, str] = json.load(f)
        with _opendata('board.json') as f:
            self.LS: Dict[str, List[str]] = json.load(f)
        with _opendata('other.json') as f:
            self.PCINFO: Dict[str, dict] = json.load(f)
        with _opendata('errors.json') as f:
            self.ERRORS: List[str] = json.load(f)
        with _opendata('helpindex.json') as f:
            self.HELPINDEX: Dict[str, Union[str, dict]] = json.load(f)


def _opendata(filenm: str) -> TextIO:
    """Open data file.

    Arguments:
        filenm {str} -- name of file to be opened

    Returns:
        file -- opened file
    """

    import os
    cwd = os.path.dirname(__file__)
    filepath = os.path.join(cwd, f'../datafiles/{filenm}')
    return open(filepath)
