import os

from kivy.uix.screenmanager import Screen

__all__ = [
    "MainScreen",
    "HelpScreen",
]


class MainScreen(Screen):
    pass


class HelpScreen(Screen):
    """The screen for displaying help files.

    :ivar text: text of help file
    """

    def __init__(self, help_file="main", **kwargs):
        """Initialise instance of HelpScreen.

        :param help_file: name of help file to load
        :param kwargs: Kivy keyword arguments
        """
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(
            script_dir,
            f'../shogi/helpfiles/{help_file}.rst'
        )
        with open(file_path) as f:
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
                pass  # TODO: Interactive visual menu support
        self.manager.current = text

    def focus_input(self):
        self.ids['input'].focus = True
