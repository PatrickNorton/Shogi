from kivy.properties import NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen

from .privates import _open_help

__all__ = [
    "MainScreen",
    "HelpScreen",
]


class MainScreen(Screen):
    """The class representing the main screen.

    :cvar board_size: size of board
    :cvar space_size: size of space
    """
    board_size = NumericProperty(0)
    space_size = NumericProperty(0)

    def focus_input(self):
        input_box = self.ids['input']
        if not input_box.focus:
            input_box.focus = True
        else:
            input_box.focus = False


class HelpScreen(Screen):
    """The screen for displaying help files.

    :ivar text: text of help file
    """

    help_file = StringProperty("main")
    text = StringProperty(None)

    def __init__(self, **kwargs):
        """Initialise instance of HelpScreen.

        :param help_file: name of help file to load
        :param kwargs: Kivy keyword arguments
        """
        super().__init__(**kwargs)
        file_name = f"{self.help_file}.rst"
        with _open_help(file_name) as f:
            self.text = f.read()

    def text_entered(self, text: str):
        """Actions for when text was entered into the prompt.

        Different actions
        -----------------

        Text in the list of current screen names:
            Jumps to that screen
        Text is a valid screen name:
            Adds that screen and changes to it
        Text is not a valid screen:
            Puts "file not found" in the prompt

        :param text: text entered
        """
        if text not in self.manager.screen_names:
            try:
                self.manager.add_widget(HelpScreen(help_file=text, name=text))
            except FileNotFoundError:
                self.ids['input'].text = 'File not found'
                # TODO: Interactive visual menu support
            else:
                self.manager.current = text
        else:
            self.manager.current = text

    def focus_input(self):
        self.ids['input'].focus = not self.ids['input'].focus


class HelpMenuScreen(Screen):
    pass
