import json
from .privates import _opendata, _flatten_dict

__all__ = [
    "getfile"
]

def getfile(filenm):
    with _opendata('helpindex.json') as f:
        filedict = json.load(f)
    for key, value in filedict['pieces'].items():
        promkey = '+'+key
        if isinstance(value, dict):
            filedict['pieces'][promkey] = filedict['pieces'][key]['promoted']
            filedict['pieces'][key] = filedict['pieces'][key]['unpromoted']
    _flatten_dict(filedict)
