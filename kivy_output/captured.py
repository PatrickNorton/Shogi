from kivy.uix.gridlayout import GridLayout

import shogi

from .capturedsquare import CapturedSquare

__all__ = [
    "CapturedGrid"
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
        self.ordered_children = self.children[::-1]

    def update(
            self,
            current_board: shogi.Board,
            color: shogi.Color
    ):
        """Update square.

        :param current_board: current board
        :param color: color of grid layout
        """
        children = self.ordered_children
        captured_pieces = current_board.captured[color]
        for space in children:
            space.remove_piece()
        for space, occupant in zip(children, captured_pieces):
            space.give_piece(occupant)

    def space_pressed(
            self,
            position: int,
            is_highlighted: bool
    ):
        """A space of the grid was pressed.

        :param position: position of square within grid
        :param is_highlighted: if the space is highlighted
        """
        self.parent.captured_press(
            self.ordered_children[position].occupant,
            is_highlighted
        )

    def un_light_all(self):
        """Un light all sub-spaces of self."""
        for x in self.children:
            x.un_light()
