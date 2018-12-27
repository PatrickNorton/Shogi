import json

__all__ = [
    "_infocls",
    "_opendata"
]

class _infocls:
    def __init__(self):
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
    import os
    cwd = os.path.dirname(__file__)
    filepath = os.path.join(cwd, f'../datafiles/{filenm}')
    return open(filepath)
