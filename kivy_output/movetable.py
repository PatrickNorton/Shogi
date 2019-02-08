from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout

import string

__all__ = [
    "MoveBox",
    "MoveGrid",
]


class MoveBox(FloatLayout):
    layout_content = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(
            lambda _: self.layout_content.bind(
                minimum_height=self.layout_content.setter('height')
            )
        )

    def add_move(self, move):
        self.ids['layout_content'].add_move(move)


class MoveGrid(GridLayout):
    box_amount = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boxes = []

    def add_move(self, move):
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
        a = Button()
        self.add_widget(a)
        self.boxes.append(a)
