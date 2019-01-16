from kivy.app import App
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import Screen

import shogi

from .core import AppCore

__all__ = [
    "ShogiBoard",
    "MainScreen",
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