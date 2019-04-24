from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

__all__ = [
    "NumberLayout",
    "NumButton",
]


class NumberLayout(BoxLayout):
    """Grid to hold the numbers for location."""
    def __init__(self, **kwargs):
        """Initialise instance of NumberLayout.

        :param kwargs: kivy keyword arguments
        """
        super().__init__(**kwargs)
        Clock.schedule_once(self._setup_subwidgets, 0)

    def _setup_subwidgets(self, _):
        """Set up the widgets that hold the numbers.

        :param _: Parameter passed for no good reason by Kivy
        """
        types_dict = {
            'horizontal': '123456789'[::-1],
            'vertical': 'abcdefghi'
        }
        to_display = types_dict[self.orientation]
        for index, letter in enumerate(to_display):
            self.add_widget(NumButton(text=letter), index=index)


class NumButton(Button):
    """Class for the numbers on the side of the board."""
    pass
