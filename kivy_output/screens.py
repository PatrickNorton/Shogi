from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen

from .privates import _open_help

__all__ = [
    "MainScreen",
    "HelpScreen",
]


class MainScreen(Screen):
    board_size = NumericProperty(0)
    space_size = NumericProperty(0)


class HelpScreen(Screen):
    """The screen for displaying help files.

    :ivar text: text of help file
    """

    def __init__(self, help_file="main", **kwargs):
        """Initialise instance of HelpScreen.

        :param help_file: name of help file to load
        :param kwargs: Kivy keyword arguments
        """
        file_name = f"{help_file}.rst"
        with _open_help(file_name) as f:
            self.text = f.read()
        super().__init__(**kwargs)

    def text_entered(self, text: str):
        """Actions for when text was entered into the prompt.

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
        self.ids['input'].focus = True


class HelpMenuScreen(Screen):
    pass
