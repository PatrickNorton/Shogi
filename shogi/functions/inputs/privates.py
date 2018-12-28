import json

__all__ = [
    "_flatten_dict",
    "_opendata",
    "_openhelp",
    "_getfile"
]


def _flatten_dict(d):
    """Flatten a dictionary.

    Arguments:
        d {dict} -- dictionary to be flattened

    Returns:
        dict -- flattened dictionary
    """

    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in _flatten_dict(value).items():
                    yield key + "." + subkey, subvalue
            else:
                yield key, value

    return dict(items())


def _opendata(filenm):
    """Open data file.

    Arguments:
        filenm {str} -- relative path (from datafiles) of file

    Returns:
        file -- opened data file
    """

    import os
    cwd = os.path.dirname(__file__)
    filepath = os.path.join(cwd, f'../../datafiles/{filenm}')
    return open(filepath)


def _openhelp(filenm):
    """Open help file.

    Arguments:
        filenm {str} -- relative path (from helpfiles) of file

    Returns:
        file -- opened help file
    """

    import os
    cwd = os.path.dirname(__file__)
    filepath = os.path.join(cwd, f'../helpfiles/{filenm}')
    piecepath = os.path.join(cwd, '../helpfiles/pieces')
    if filenm in os.listdir(piecepath):
        piecepath = os.path.join(piecepath, filenm)
        return open(piecepath)
    else:
        return open(filepath)


def _getfile(filenm):
    """Get helpfile path from name

    Arguments:
        filenm {str} -- "public" name of file
    """

    with _opendata('helpindex.json') as f:
        filedict = json.load(f)
    for key, value in filedict['pieces'].items():
        promkey = '+'+key
        if isinstance(value, dict):
            filedict['pieces'][promkey] = filedict['pieces'][key]['promoted']
            filedict['pieces'][key] = filedict['pieces'][key]['unpromoted']
    _flatten_dict(filedict)
