import json

__all__ = [
    "_flatten_dict",
    "_opendata",
    "_openhelp",
    "_geterrors",
    "_getfile"
]

def _flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in _flatten_dict(value).items():
                    yield key + "." + subkey, subvalue
            else:
                yield key, value

    return dict(items())


def _opendata(filenm):
    import os
    cwd = os.path.dirname(__file__)
    filepath = os.path.join(cwd, f'../datafiles/{filenm}')
    return open(filepath)


def _openhelp(filenm):
    import os
    cwd = os.path.dirname(__file__)
    filepath = os.path.join(cwd, f'../helpfiles/{filenm}')
    piecepath = os.path.join(cwd, '../helpfiles/pieces')
    if filenm in os.listdir(piecepath):
        piecepath = os.path.join(piecepath, filenm)
        return open(piecepath)
    else:
        return open(filepath)


def _geterrors():
    with _opendata('errors.json') as f:
        return json.load(f)


def _getfile(filenm):
    with _opendata('helpindex.json') as f:
        filedict = json.load(f)
    for key, value in filedict['pieces'].items():
        promkey = '+'+key
        if isinstance(value, dict):
            filedict['pieces'][promkey] = filedict['pieces'][key]['promoted']
            filedict['pieces'][key] = filedict['pieces'][key]['unpromoted']
    _flatten_dict(filedict)