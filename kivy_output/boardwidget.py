from typing import Dict

from kivy.uix.gridlayout import GridLayout

import shogi
from .boardsquare import BoardSquare

__all__ = [
    "ChessBoard",
]


class ChessBoard(GridLayout):
    """The class that holds the chess board on screen.

    :ivar children_dict: dict of coordinates -> squares
    :ivar board: current game board
    :ivar make_move: if next click makes a move or highlights
    :ivar move_from: space to move from
    :ivar in_check: list of pieces checking each king
    """

    def __init__(self, **kwargs):
        """Initialise instance of ChessBoard.

        :param kwargs: keyword arguments to pass
        """
        board = shogi.Board()
        super().__init__(cols=9, rows=9, **kwargs)
        # self.board: shogi.Board = shogi.Board()
        for x, y in board.iterate():
            coordinate = shogi.AbsoluteCoord((x, y))
            square = BoardSquare(coordinate, board[coordinate])
            self.add_widget(square)
        self.children_dict: Dict[shogi.AbsoluteCoord, BoardSquare] = {
            x.board_position: x for x in self.children
        }

    def space_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Light or make move when a specific space is pressed.

        This is simply a delegate call to the board_pressed method
        of its parent, and does not do any processing itself.

        :param coordinate: location of pressed square
        """
        self.parent.board_pressed(coordinate)

    def update_squares(self, *to_update: shogi.AbsoluteCoord):
        """Update specific squares.

        This, given an iterable of coordinates, updates their
        corresponding board positions.

        :param to_update: list of squares to update
        """
        for coordinate in to_update:
            space = self.children_dict[coordinate]
            space.text = space.set_string(self.board[coordinate])

    def get_pieces(self, position: shogi.AbsoluteCoord) -> shogi.Piece:
        """Get piece at location.

        :param position: position to get piece at
        :return: piece at location
        """
        return self.board[position]

    def un_light_all(self):
        """Un-highlight all squares."""
        self.parent.un_light_captured()
        highlighted_spaces = {
            x: y for x, y in self.children_dict.items() if y.is_highlighted
        }
        for space in highlighted_spaces.values():
            space.un_light()

    @property
    def board(self):
        return self.parent.board
