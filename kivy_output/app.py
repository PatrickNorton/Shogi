from pathlib import Path
from typing import List

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex

import shogi
from .boardsquare import BoardSquare
from .boardwidget import ChessBoard
from .captured import CapturedGrid
from .capturedsquare import CapturedSquare
from .core import AppCore
from .inputs import HelpRst, PromotionWindow, MateWindow, HelpText
from .movetable import MoveGrid, MoveBox
from .numbers import NumberLayout
from .screens import HelpScreen, MainScreen

__all__ = [
    "ShogiBoard",
]

# Configure kivy to not quit when Esc is pressed, so it can be used
# for the interactive help prompt
Config.set('kivy', 'exit_on_escape', '0')
Config.write()
resource_add_path(Path(__file__).parent.parent / "images")


class ShogiBoard(App):
    """Main class for the entire app.

    This app implicitly loads the ShogiBoard.kv file.

    :ivar self.board: current game board
    """

    def __init__(self, **kwargs):
        """Initialise instance of ShogiBoard.

        :param kwargs: Kivy keyword arguments
        """
        super().__init__(**kwargs)
        self.board = shogi.Board()
        Window.bind(on_keyboard=self._on_keyboard)
        for cls in (BoardSquare, ChessBoard, CapturedGrid, CapturedSquare,
                    AppCore, HelpRst, PromotionWindow, MateWindow, HelpText,
                    NumberLayout, MoveGrid, MoveBox):
            Factory.register(cls.__name__, cls=cls)

    @staticmethod
    def get_background_color():
        """Get standard background color."""
        return get_color_from_hex("#1e2022")

    def build(self):
        """Build and run the application.

        :return: ScreenManager for the entire app
        """
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        Clock.schedule_once(
            lambda x: sm.add_widget(HelpScreen(name='help')),
            0
        )
        return sm

    def _on_keyboard(
            self,
            _instance,
            key: int,
            _scan_code: int,
            code_point: str,
            modifiers: List[str]
    ):
        """Keyboard binding code.

        This runs the keyboard shortcuts necessary to make the app
        run properly.

        :param _instance: instance of window, unused and unknown
        :param key: integer of key pressed
        :param _scan_code: scanned code, unused
        :param code_point: text of pressed key
        :param modifiers: list of modifiers pressed in conjunction
        """
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
