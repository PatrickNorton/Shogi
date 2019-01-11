from kivy.app import App, Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button


class AppCore(Widget):
    pass


class ChessBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(rows=9, **kwargs)
        for _ in range(81):
            self.add_widget(BoardSquare())


class Test(Widget):
    pass


class BoardSquare(Button):
    def on_press(self):
        self.text = 'hi'

    def on_release(self):
        self.text = ''


class ShogiBoard(App):
    def build(self):
        return AppCore()


if __name__ == "__main__":
    ShogiBoard().run()
