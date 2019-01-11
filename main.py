from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from shogi import AbsoluteCoord


class AppCore(Widget):
    @staticmethod
    def get_background_color():
        return get_color_from_hex("#1e2022")


class ChessBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=9, rows=9, **kwargs)
        for x in range(81):
            self.add_widget(BoardSquare(AbsoluteCoord((8-x % 9, x//9))))


class BoardSquare(Button):
    def __init__(self, position, **kwargs):
        self.board_position = position
        super().__init__(**kwargs)

    def get_position(self): return str(self.board_position)


class ShogiBoard(App):
    def build(self):
        return AppCore()


if __name__ == "__main__":
    ShogiBoard().run()
