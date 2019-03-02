from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import get_color_from_hex

from .bindings import Keybindings
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
        register_classes()
        Clock.schedule_once(self._keyboard_setup)

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

    @property
    def core(self):
        return self.root.get_screen('main').ids['core']

    @property
    def main_screen(self):
        return self.root.get_screen('main')

    def switch_help(self):
        self.root.transition.direction = 'left'
        self.root.current = 'help'

    def switch_main(self):
        self.root.transition.direction = 'right'
        self.root.current = 'main'

    def _keyboard_setup(self, _):
        self.keybindings = Keybindings(self)
        Window.bind(on_keyboard=self.keybindings.get_key)
