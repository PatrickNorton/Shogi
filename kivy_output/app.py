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
    background = StringProperty("#1e2022")

    def __init__(self, **kwargs):
        """Initialise instance of ShogiBoard.

        :param kwargs: Kivy keyword arguments
        """
        super().__init__(**kwargs)
        # Register all the classes with Kivy, so it knows where
        # everything is
        register_classes()
        # Setup all those pesky variables that can't exist until after
        # initialisation
        Clock.schedule_once(self._keyboard_setup)

    def build(self):
        """Build and run the application.

        :return: ScreenManager for the entire app
        """
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(HelpScreen(name='help'))
        return sm

    @property
    def background_color(self):
        return get_color_from_hex(self.background)

    @property
    def core(self):
        return self.root.get_screen('main').ids['core']

    @property
    def main_screen(self):
        return self.root.get_screen('main')

    def switch_help(self):
        """Switch to the help screen.

        Used for keybindings.
        """
        self.root.transition.direction = 'left'
        self.root.current = 'help'

    def switch_main(self):
        """Switch to the main screen.

        Used for keybindings.
        """
        self.root.transition.direction = 'right'
        self.root.current = 'main'

    def focus_input(self):
        """Focus the input on the current screen.

        Used for keybindings.
        """
        self.root.current_screen.focus_input()

    def _keyboard_setup(self, _):
        self.keybindings = Keybindings(self)
        Window.bind(on_keyboard=self.keybindings.key_action)
