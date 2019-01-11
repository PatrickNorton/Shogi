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
        pressed_square = self.children_dict[coordinate]
        highlighted_spaces = {
            x: y for x, y in self.children_dict.items() if y.is_highlighted
        }
        do_highlight = pressed_square.is_highlighted
        for space in highlighted_spaces.values():
            space.un_light()
        if not do_highlight:
            valid_moves = pressed_square.valid_moves(self.board)
            valid_spaces = [
                self.children_dict[x] for x in valid_moves
            ]
            for space in valid_spaces:
                space.light()
            pressed_square.light()

    def make_moves(self, current, to):
        try:
            shogi.move_check_2(self.board, (current, to))
        except shogi.IllegalMove:
            pass
        else:
            self.board.move(current, to)
            self.update_squares((current, to))

    def update_squares(self, to_update):
        for coordinate in to_update:
            space = self.children_dict[coordinate]
            space.set_image(self.board[coordinate])

    def get_piece(self, position): return self.board[position]


class BoardSquare(Button):
    def __init__(self, position, **kwargs):
        self.board_position = position
        self.is_highlighted = False
        super().__init__(**kwargs)

    def get_position(self):
        pos = shogi.Board()[self.board_position]
        return str(pos) if pos else ''

    def light(self):
        self.background_normal = "./images/Highlighted space.jpg"
        self.background_down = "./images/Highlighted space.jpg"
        self.color = 0, 0, 0, 1
        self.is_highlighted = True

    def un_light(self):
        self.background_normal = "./images/Light square.jpg"
        self.background_down = "./images/Light square.jpg"
        self.color = 1, 1, 1, 1
        self.is_highlighted = False

    def set_image(self, piece):
        return str(piece)

    def valid_moves(self, current_board):
        current_piece = current_board[self.board_position]
        valid_spaces = []
        for dir_number in range(8):
            direction = shogi.Direction(dir_number)
            direction_spaces = current_piece.valid_spaces(direction)
            # shogi.move_check_2(current_board, (self.board_position, direction_spaces[0]))
            direction_spaces = shogi.test_spaces(
                current_board,
                self.board_position,
                direction_spaces
            )
            valid_spaces += direction_spaces
        return valid_spaces


class ShogiBoard(App):
    def build(self):
        return AppCore()


if __name__ == "__main__":
    ShogiBoard().run()
