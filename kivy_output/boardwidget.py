from kivy.uix.gridlayout import GridLayout

from typing import Dict

import shogi

from .boardsquare import BoardSquare

__all__ = [
    "ChessBoard"
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
        for x in range(81):
            coordinate = shogi.AbsoluteCoord((x % 9, x//9))
            square = BoardSquare(coordinate, board[coordinate])
            self.add_widget(square)
        self.children_dict: Dict[shogi.AbsoluteCoord, BoardSquare] = {
            x.board_position: x for x in self.children
        }

    def space_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Light or make move when a specific space is pressed.

        :param coordinate: location of pressed square
        """
        self.parent.board_pressed(coordinate)
        """
        if not self.parent.make_move or self.parent.move_from == coordinate:
            self.parent.light_moves(coordinate)
        else:
            self.parent.make_moves(self.parent.move_from, coordinate)
        """

    def update_squares(self, *to_update: shogi.AbsoluteCoord):
        """Update specific squares.

        :param to_update: list of squares to update
        """
        for coordinate in to_update:
            space = self.children_dict[coordinate]
            space.text = space.set_string(self.board[coordinate])

    def get_piece(self, position: shogi.AbsoluteCoord) -> shogi.Piece:
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
        self.parent.make_move = False

    def in_play_light(self, piece):
        self.un_light_all()
        empty_children = {
            x: y for x, y in self.children_dict.items() if not y.text
        }
        if piece.color == self.board.current_player:
            for space, x in empty_children.items():
                promotion_zones = ((0, 1, 2), (8, 7, 6))
                player_int = int(piece.color)
                try:
                    index = promotion_zones[player_int].index(space.y)
                except ValueError:
                    x.light()
                else:
                    if index >= piece.auto_promote:
                        x.light()
            self.parent.make_move = True

    @property
    def board(self):
        return self.parent.board
