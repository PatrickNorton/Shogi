from kivy.uix.popup import Popup
from kivy.uix.rst import RstDocument
from kivy.uix.textinput import TextInput

__all__ = [
    "HelpRst",
    "PromotionWindow",
    "MateWindow",
    "HelpText",
]

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