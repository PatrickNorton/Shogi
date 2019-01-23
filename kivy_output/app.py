from typing import List

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex

import shogi

from .screens import HelpScreen, MainScreen

__all__ = [
    "ShogiBoard",
]


# Configure kivy to not quit when Esc is pressed, so it can be used
# for the interactive help prompt
Config.set('kivy', 'exit_on_escape', '0')
Config.write()


class ShogiBoard(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = shogi.Board()
        Window.bind(on_keyboard=self._on_keyboard)

    @staticmethod
    def get_background_color():
        """Get standard background color."""
        return get_color_from_hex("#1e2022")

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(HelpScreen(name='help'))
        return sm

    def _on_keyboard(
            self,
            _instance,
            key: int,
            _scan_code: int,
            code_point: str,
            modifiers: List[str]
    ):
        is_meta_modifier = (modifiers == ['meta'])
        is_help_screen = isinstance(self.root.current_screen, HelpScreen)
        if modifiers:
            if is_meta_modifier and code_point == 'w':
                self.stop()
            if is_meta_modifier and code_point == '/':
                if self.root.current == 'main':
                    self.root.transition.direction = 'left'
                    self.root.current = 'help'
                elif is_help_screen:
                    self.root.transition.direction = 'right'
                    self.root.current = 'main'
            if is_meta_modifier and key == 276:
                if is_help_screen:
                    self.root.transition.direction = 'right'
                    self.root.current = 'main'
        else:
            if key == 27:
                if is_help_screen:
                    self.root.current_screen.focus_input()
