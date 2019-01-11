from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
import shogi


class AppCore(Widget):
    @staticmethod
    def get_background_color():
        return get_color_from_hex("#1e2022")


class ChessBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=9, rows=9, **kwargs)
        for x in range(81):
            square = BoardSquare(shogi.AbsoluteCoord((8-x % 9, x//9)))
            self.add_widget(square)
        self.children_dict = {x.board_position: x for x in self.children}
        self.board = shogi.Board()

    def space_pressed(self, coordinate):
        the_space = self.children_dict[coordinate]
        highlighted_spaces = {
            x: y for x, y in self.children_dict.items() if y.is_highlighted and y != the_space
        }
        if not the_space.is_highlighted:
            the_space.light()
        else:
            the_space.un_light()
        for a_space in highlighted_spaces.values():
            a_space.un_light()


class BoardSquare(Button):
    def __init__(self, position, **kwargs):
        self.board_position = position
        self.is_highlighted = False
        super().__init__(**kwargs)

    def get_position(self): return str(self.board_position)

    def light(self):
        self.background_normal = "./images/Highlighted space.jpg"
        self.background_down = "./images/Highlighted space.jpg"
        self.is_highlighted = True

    def un_light(self):
        self.background_normal = "./images/Light square.jpg"
        self.background_down = "./images/Light square.jpg"
        self.is_highlighted = False


class ShogiBoard(App):
    def build(self):
        return AppCore()


if __name__ == "__main__":
    ShogiBoard().run()
