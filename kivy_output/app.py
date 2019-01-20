from kivy.app import App
from kivy.clock import Clock
from kivy.properties import DictProperty
from kivy.uix.popup import Popup
from kivy.uix.rst import RstDocument
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.utils import get_color_from_hex

import shogi

__all__ = [
    "ShogiBoard",
    "MainScreen",
    "PromotionWindow",
    "MateWindow",
]


class ShogiBoard(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = shogi.Board()

    @staticmethod
    def get_background_color():
        """Get standard background color."""
        return get_color_from_hex("#1e2022")

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(HelpScreen(name='help'))
        return sm


class MainScreen(Screen):
    pass


class HelpScreen(Screen):
    with open("./shogi/helpfiles/main.txt") as f:
        text = f.read()


class HelpRst(RstDocument):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colors['paragraph'] = "eeeeee"
        self.colors['background'] = '1e2022'


class PromotionWindow(Popup):
    def __init__(self, to_highlight, caller=None, **kwargs):
        self.caller = caller
        self.to_highlight = to_highlight
        super().__init__(**kwargs)

    def open(self, *largs, **kwargs):
        super().open(*largs, **kwargs)

    def child_pressed(self, promote):
        self.caller.to_promote = promote
        self.dismiss()


class MateWindow(Popup):
    pass