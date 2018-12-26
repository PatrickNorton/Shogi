import json
from .privates import _opendata

__all__ = [
    "geterrors"
]

def geterrors():
    with _opendata('errors.json') as f:
        return json.load(f)
