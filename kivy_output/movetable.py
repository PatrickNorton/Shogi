from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout

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


class MoveGrid(GridLayout):
    """Grid layout holding the moves.

    """
    box_amount = NumericProperty(0)

    def __init__(self, **kwargs):
        """Initialise instance of MoveGrid.

        :param kwargs: kivy keyword arguments
        """
        super().__init__(**kwargs)
        self.boxes = []

    def add_move(self, move: str):
        """Add a move to the grid.

        :param move: string of move to be added
        """
        if not self.boxes or self.boxes[-1].text:
            self.add_box()
            self.add_box()
            self.boxes[-2].text = move
            return
        for box in self.boxes:
            if not box.text:
                box.text = move
                break

    def add_box(self):
        """Add a box to self.
        """
        a = Button()
        self.add_widget(a)
        self.boxes.append(a)
