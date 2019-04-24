from typing import Dict, Optional
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
        # Temporary board passed at setup time.
        board = shogi.Board()
        super().__init__(cols=board.y_size, rows=board.x_size, **kwargs)
        # Map of coordinates to screen squares
        self.children_dict = {}
        self.set_up = False
        # IMPORTANT: self.set_up_squares should be called by AppCore
        # sometime during setup.
        # If something is going wrong during setup, try looking at
        # that, if you can't find the error

    def space_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Light or make move when a specific space is pressed.

        This is simply a delegate call to the board_pressed method
        of its parent, and does not do any processing itself.

        :param coordinate: location of pressed square
        """
        self.parent.board_pressed(coordinate)

    def update_squares(self, *to_update: Optional[shogi.AbsoluteCoord]):
        """Update specific squares.

        This, given an iterable of coordinates, updates their
        corresponding board positions.

        :param to_update: list of squares to update
        """
        for coordinate in to_update:
            # For e.g. dropping moves, when move_from is None
            if coordinate is None:
                continue
            space = self.children_dict[coordinate]
            # Set the string of each updated space to the occupant
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
        for space in self.children_dict.values():
            if space.is_highlighted:
                space.un_light()

    @property
    def board(self):
        return self.parent.board

    def set_up_squares(self, *_):
        """By the accursed gods of Kivy, if I want to not create
        multiple shogi.Board instances to set this stuff up, I need
        to create this function to do it for me.
        Call this when you need to actually set up the widget, but
        ***ONLY CALL IT ONCE***
        It will raise a RuntimeError otherwise.

        :param _: Whatever variables kivy passes to this thing
        """
        if self.set_up:
            raise RuntimeError("set_up_squares should not be run twice")
        self.set_up = True
        # Add a space for each square of the board, with occupant
        for x, y in self.parent.board.iterate():
            coordinate = shogi.AbsoluteCoord((x, y))
            self.add_widget(BoardSquare(coordinate, self.parent.board[x, y]))
        self.children_dict: Dict[shogi.AbsoluteCoord, BoardSquare] = {
            x.board_position: x for x in self.children
        }
