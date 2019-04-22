from itertools import zip_longest
from typing import List

from kivy.uix.gridlayout import GridLayout

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
        # Add squares for the captured pieces
        for x in range(8):
            self.add_widget(CapturedSquare(x))
        # List of squares in order, from top left to bottom right
        self.ordered_children: List[CapturedSquare] = self.children[::-1]

    def update(
            self,
            current_board: shogi.Board,
            color: shogi.Color
    ):
        """Update squares to match the captured list.

        :param current_board: current board
        :param color: color of grid layout
        """
        captured_pieces = current_board.captured[color]
        # Go through the spaces, and update them if their occupants
        # have changed from their current states.
        for space, occupant in zip_longest(
            # zip_longest is necessary so that if the number of
            # captured pieces decreases, all the squares still update
            self.ordered_children, captured_pieces,
            fillvalue=shogi.NoPiece()
        ):
            # If the space goes from occupied to unoccupied, remove
            # the piece
            if space.occupant and not occupant:
                space.remove_piece()
            # If the square changes occupants, update that
            elif space.occupant != occupant:
                # This *can* be called to change pieces, not just add
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
