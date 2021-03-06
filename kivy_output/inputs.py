from kivy.properties import ObjectProperty
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
    """The help rst document.

    This is used for the help file display, and contains a custom
    color scheme to match the theme of the board.
    """

    def __init__(self, **kwargs):
        """Initialise instance of HelpRst.

        :param kwargs: Kivy keyword arguments
        """
        super().__init__(**kwargs)
        self.colors['paragraph'] = "#eeeeeeff"
        self.colors['background'] = '#1e2022ff'
        self.colors['bullet'] = "#ffffffff"


class PromotionWindow(Popup):
    """Popup window asking if a promotion is wanted.

    Note: This **requires** a caller with a to_promote method.

    :ivar caller: object that called the popup window
    """

    caller = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Initialise instance of PromotionWindow.

        :param caller: object that called the window
        :param kwargs: Kivy keyword arguments
        """
        super().__init__(**kwargs)

    def child_pressed(self, promote: bool):
        """A child button of this widget was pressed.

        This runs the caller's to_promote method, and dismisses
        itself.

        :param promote: if the piece should be promoted
        """
        self.caller.to_promote = promote
        self.dismiss()


class MateWindow(Popup):
    """The window for when checkmate happens."""
    pass


class HelpText(TextInput):
    pass


class MainText(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(focus=self._on_focus_change)

    def _on_focus_change(self, *_):
        if self.focus:
            self.background_color = (.25, .25, .25, 1)
        else:
            self.background_color = (0, 0, 0, 0)
            self.text = ''
