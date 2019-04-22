from typing import Dict, Optional

import shogi

__all__ = [
    "GameState",
]


class GameState:
    def __init__(self):
        # Current state: whether next click highlights or moves
        self.make_move: bool = False
        # Space where a player would move from
        self.move_from: shogi.AbsoluteCoord = shogi.NullCoord()
        # Pieces checking each king, arranged by color
        self.in_check: Dict[shogi.Color, shogi.CoordSet] = {
            shogi.Color(0): set(),
            shogi.Color(1): set()
        }
        # Piece to be dropped
        self.to_add: shogi.Piece = shogi.NoPiece()
        # Whether or not to promote the piece
        self.to_promote: Optional[bool] = None

    def post_turn(self):
        self.make_move = False
        self.move_from = shogi.NullCoord()
        self.to_add = None
        self.to_promote = None
