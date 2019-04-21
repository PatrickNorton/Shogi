from kivy.uix.gridlayout import GridLayout
from typing import List

import shogi
from .capturedsquare import CapturedSquare

__all__ = [
    "CapturedGrid",
]


class CapturedGrid(GridLayout):
    """Grid containing captured pieces."""

    def __init__(self, **kwargs):
        """Initialise instance of CapturedGrid.

        :param kwargs: keyword arguments to pass
        """
        super().__init__(cols=4, rows=2, **kwargs)
        for x in range(8):
            self.add_widget(CapturedSquare(x))
        self.ordered_children: List[CapturedSquare] = self.children[::-1]

    def update(
            self,
            current_board: shogi.Board,
            color: shogi.Color
    ):
        """Update square.

        For now, this removes all pieces from the squares,
        and then reassigns them according to how they were
        given.
        This should be changed.

        :param current_board: current board
        :param color: color of grid layout
        """
        captured_pieces = current_board.captured[color]
        for space in self.ordered_children:
            space.remove_piece()
        for space, occupant in zip(self.ordered_children, captured_pieces):
            space.give_piece(occupant)

    def space_pressed(self, position: int):
        """A space of the grid was pressed.

        :param position: position of square within grid
        """
        self.parent.captured_press(self.ordered_children[position])

    def un_light_all(self):
        """Un light all sub-spaces of self."""
        for x in self.children:
            if x.is_highlighted:
                x.un_light()
