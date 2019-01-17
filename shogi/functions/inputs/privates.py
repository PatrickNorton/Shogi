import json

from typing import IO, Dict

__all__ = [
    "_flatten_dict",
    "_open_data",
    "_open_help",
    "_getfile"
]


def _flatten_dict(d: dict) -> dict:
    """Flatten a dictionary.

    :param d: dictionary to be flattened
    :return: flattened dictionary
    """

    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for sub_key, sub_value in _flatten_dict(value).items():
                    yield key + "." + sub_key, sub_value
            else:
                yield key, value

    return dict(items())


def _open_data(file_name: str) -> IO[str]:
    """Open data file.

    :param file_name: relative path of file
    :return: opened data file
    """

    import os
    cwd = os.path.dirname(__file__)
    file_path = os.path.join(cwd, f'../../datafiles/{file_name}')
    return open(file_path)


def _open_help(file_name: str) -> IO[str]:
    """Open help file.

    :param file_name: relative path of file
    :return: opened help file
    """

    import os
    cwd = os.path.dirname(__file__)
    file_path = os.path.join(cwd, f'../helpfiles/{file_name}')
    piece_path = os.path.join(cwd, '../helpfiles/pieces')
    if file_name in os.listdir(piece_path):
        piece_path = os.path.join(piece_path, file_name)
        return open(piece_path)
    else:
        return open(file_path)


def _getfile(file_name: Dict[str, str]) -> str:
    """Get helpfile path from name

    :param file_name: "public" name of file
    :return: path to file
    """

    with _open_data('helpindex.json') as f:
        file_dict = json.load(f)
    for key, value in file_dict['pieces'].items():
        promotion_key = '+' + key
        if isinstance(value, dict):
            promoted_value = file_dict['pieces'][key]['promoted']
            file_dict['pieces'][promotion_key] = promoted_value
            file_dict['pieces'][key] = file_dict['pieces'][key]['unpromoted']
    _flatten_dict(file_dict)
    return file_dict[file_name]
