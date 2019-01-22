import os

from typing import List

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.rst import RstDocument
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

import shogi

__all__ = [
    "ShogiBoard",
    "MainScreen",
    "PromotionWindow",
    "MateWindow",
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
        if modifiers:
            if modifiers == ['meta'] and code_point == 'w':
                self.stop()
            if modifiers == ['meta'] and code_point == '/':
                if self.root.current == 'main':
                    self.root.transition.direction = 'left'
                    self.root.current = 'help'
                elif self.root.current == 'help':
                    self.root.transition.direction = 'right'
                    self.root.current = 'main'
        else:
            if key == 27:
                if isinstance(self.root.current_screen, HelpScreen):
                    self.root.current_screen.focus_input()


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


class HelpRst(RstDocument):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colors['paragraph'] = "#eeeeeeff"
        self.colors['background'] = '#1e2022ff'
        self.colors['bullet'] = "#ffffffff"


class PromotionWindow(Popup):
    def __init__(self, to_highlight, caller=None, **kwargs):
        self.caller = caller
        self.to_highlight = to_highlight
        super().__init__(**kwargs)

    def open(self, *largs, **kwargs):
        super().open(*largs, **kwargs)

    def child_pressed(self, promote):
        self.caller.to_promote = promote
        self.dismiss()


class MateWindow(Popup):
    pass


class HelpText(TextInput):
    pass
