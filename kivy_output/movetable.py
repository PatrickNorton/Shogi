from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout

import shogi

__all__ = [
    "MoveBox",
    "MoveGrid",
]


class MoveBox(FloatLayout):
    """The box that holds the table of moves.

    This needs pretty much no functionality besides what is already
    there, so it shouldn't change that much.
    """
    layout_content = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Initialise instance of MoveBox.

        :param kwargs: keyword arguments for kivy
        """
        super().__init__(**kwargs)
        # Set the height to what it needs to be
        Clock.schedule_once(
            lambda _: self.layout_content.bind(
                minimum_height=self.layout_content.setter('height')
            )
        )

    def add_move(self, move: str):
        """Add move to the list.

        :param move: move to be added
        """
        self.ids['layout_content'].add_move(move)

    def remove_last(self):
        """Remove last move from list.
        """
        self.ids['layout_content'].remove_last()


class MoveGrid(GridLayout):
    """Grid layout holding the moves.

    :ivar boxes: list of MoveBoxes holding a turn
    """
    box_amount = NumericProperty(0)

    def __init__(self, **kwargs):
        """Initialise instance of MoveGrid.

        :param kwargs: kivy keyword arguments
        """
        super().__init__(**kwargs)
        self.boxes = []

    def add_move(self, move: shogi.Move):
        """Add a move to the grid.

        :param move: string of move to be added
        """
        # If the bottom box is full, add a new row
        if not self.boxes or self.boxes[-1].text:
            self.add_box()
            self.add_box()
            self.boxes[-2].text = str(move)
            return
        # Add to the first empty box in the list
        for box in self.boxes:
            if not box.text:
                box.text = str(move)
                break

    def remove_last(self):
        # If the last row is empty, remove the boxes
        if not self.boxes[-1].text:
            self.boxes[-2].text = ''
            self.remove_last_box()
            self.remove_last_box()
        # Otherwise, just clear the last box
        else:
            self.boxes[-1].text = ''

    def add_box(self):
        """Add a box to self.
        """
        a = Button()
        self.add_widget(a)
        self.boxes.append(a)

    def remove_last_box(self):
        self.remove_widget(self.boxes[-1])
        del self.boxes[-1]
