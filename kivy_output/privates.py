from typing import IO
import pathlib

__all__ = [
    "_open_help",
    "_get_image_loc"
]


def _open_help(file_name: str) -> IO[str]:
    """Open help file.

    :param file_name: relative path of file
    :return: opened help file
    """

    current_dir = pathlib.Path(__file__).parent.parent
    piece_path = current_dir / 'shogi' / ' helpfiles' / 'pieces' / file_name
    if piece_path.exists():
        return open(piece_path)
    else:
        file_path = current_dir / 'shogi' / 'helpfiles' / file_name
        return open(file_path)


def _get_image_loc(file_name: str) -> str:
    """Get name of an image file in the images dir.

    :param file_name: name of file
    :return: image file
    """
    current_directory = pathlib.Path(__file__).parent
    piece_path = current_directory / '../images/pieces' / file_name
    file_path = current_directory / '../images' / file_name
    if piece_path.exists():
        return str(piece_path)
    elif file_path.exists():
        return str(piece_path)
    else:
        raise FileNotFoundError
