from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
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
        return MainScreen()


class MainScreen(Screen):
    pass


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