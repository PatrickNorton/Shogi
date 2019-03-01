import sys
from pathlib import Path
from typing import List

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex

from .screens import HelpScreen, MainScreen
from .registration import register_classes

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

    background_color = StringProperty("#1e2022")

    def __init__(self, **kwargs):
        """Initialise instance of ShogiBoard.

        :param kwargs: Kivy keyword arguments
        """
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self._on_keyboard)
        register_classes()

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
        """Keyboard binding code.

        This runs the keyboard shortcuts necessary to make the app
        run properly. Parameters starting with an underscore are not
        currently used, but passed into the function by kivy, so they
        must remain there.

        :param _instance: instance of window, unused and unknown
        :param key: integer of key pressed
        :param _scan_code: scanned code, unused
        :param code_point: text of pressed key
        :param modifiers: list of modifiers pressed in conjunction
        """
        is_mac = (sys.platform == 'darwin')
        meta = 'meta' if is_mac else 'ctrl'
        has_meta = (meta in modifiers)
        has_shift = ('shift' in modifiers)
        is_only_meta = (modifiers == [meta])
        is_help_screen = isinstance(self.root.current_screen, HelpScreen)
        is_main_screen = (self.root.current == 'main')
        if is_only_meta:
            if code_point == 'w':
                self.stop()
            if code_point == '/':
                if is_main_screen:
                    self.root.transition.direction = 'left'
                    self.root.current = 'help'
                elif is_help_screen:
                    self.root.transition.direction = 'right'
                    self.root.current = 'main'
            if code_point == 'z' and is_main_screen:
                self.root.current_screen.ids['core'].undo_last_move()
            if code_point == 'y' and is_main_screen:
                self.root.current_screen.ids['core'].redo_last_move()
            if key == 276:
                if is_help_screen:
                    self.root.transition.direction = 'right'
                    self.root.current = 'main'
        elif has_meta and has_shift:
            if code_point == 'z' and is_main_screen:
                self.root.current_screen.ids['core'].redo_last_move()
        else:
            if key == 27:
                if is_help_screen:
                    self.root.current_screen.focus_input()
