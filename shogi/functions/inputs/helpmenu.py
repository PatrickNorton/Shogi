import json
from .inputfns import getinput
from .privates import _opendata

__all__ = [
    "helpmenu"
]

def helpmenu(input_gen, window, theboard):
    with _opendata('helpindex.json') as f:
        index = json.load(f)
    while True:
        todisp = list(index)
        todisp.extend(['','',''])
        todisp.append('menu: ')
        window.render_to_terminal(todisp)
        filenm = getinput(input_gen, window, todisp)
        try:
            filenm = int(filenm)
            filenm = todisp.index(filenm)
        except ValueError:
            pass
        filepath = index[filenm]
        if isinstance(filepath, str):
            break
        elif isinstance(filepath, dict):
            index = filepath
    return filepath
