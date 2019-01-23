import os

from kivy.uix.screenmanager import Screen

__all__ = [
    "MainScreen",
    "HelpScreen",
]


class MainScreen(Screen):
    pass


class HelpScreen(Screen):
    def __init__(self, help_file="main", **kwargs):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(
            script_dir,
            f'../shogi/helpfiles/{help_file}.rst'
        )
        with open(file_path) as f:
            self.text = f.read()
        super().__init__(**kwargs)

    def text_entered(self, text: str):
        if text not in self.manager.screen_names:
            try:
                self.manager.add_widget(HelpScreen(help_file=text, name=text))
            except FileNotFoundError:
                pass  # TODO: Interactive visual menu support
        self.manager.current = text

    def focus_input(self):
        self.ids['input'].focus = True
