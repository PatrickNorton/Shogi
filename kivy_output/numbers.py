from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

__all__ = [
    "NumberLayout",
]


class NumberLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._setup_subwidgets, 0)

    def _setup_subwidgets(self, _):
        types_dict = {
            'horizontal': '123456789',
            'vertical': 'abcdefghi'
        }
        to_display = types_dict[self.orientation]
        for index, letter in enumerate(to_display):
            self.add_widget(NumButton(text=letter), index=index)


class NumButton(Button):
    pass
