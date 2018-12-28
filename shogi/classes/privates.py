import json

__all__ = [
    "_infocls",
    "_opendata"
]


class _infocls:
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
        """Initialise instance of _infocls."""

        with _opendata('moves.json') as f:
            self.MOVEDICT = json.load(f)
        with _opendata('names.json') as f:
            self.NAMEDICT = json.load(f)
        with _opendata('board.json') as f:
            self.LS = json.load(f)
        with _opendata('other.json') as f:
            self.PCINFO = json.load(f)
        with _opendata('errors.json') as f:
            self.ERRORS = json.load(f)
        with _opendata('helpindex.json') as f:
            self.HELPINDEX = json.load(f)


def _opendata(filenm):
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
