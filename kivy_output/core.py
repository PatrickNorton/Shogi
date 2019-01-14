from kivy.uix.widget import Widget

import shogi

__all__ = [
    "AppCore"
]


class AppCore(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.captured_spaces = {0: self.ids['0'], 1: self.ids['1']}

    def update_captured(self, current_board):
        for x, val in enumerate(self.captured_spaces.values()):
            val.update(current_board, shogi.Color(x))

    def captured_press(self, piece, is_highlighted):
        if not is_highlighted:
            self.ids["board"].in_play_light(piece)
        else:
            self.ids["board"].un_light_all()
            self.ids["board"].make_move = False

    def un_light_captured(self):
        self.ids['0'].un_light_all()
        self.ids['1'].un_light_all()

    def un_light_board(self):
        self.ids['board'].un_light_all()
