from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from typing import Iterable, Dict, List
import shogi

# TODO: Promotion, reconstituting captured pieces


class AppCore(Widget):
    @staticmethod
    def get_background_color():
        return get_color_from_hex("#1e2022")


class ChessBoard(GridLayout):
    """The class that holds the chess board on screen.

    :ivar children_dict: dict of coordinates -> squares
    :ivar board: current game board
    :ivar make_move: if next click makes a move or highlights
    :ivar move_from: space to move from
    :ivar in_check: list of pieces checking each king
    """
    def __init__(self, **kwargs):
        """Initialise instance of ChessBoard.

        :param kwargs: keyword arguments to pass
        """
        super().__init__(cols=9, rows=9, **kwargs)
        self.board: shogi.Board = shogi.Board()
        for x in range(81):
            coordinate = shogi.AbsoluteCoord((x % 9, x//9))
            square = BoardSquare(coordinate, self.board[coordinate])
            self.add_widget(square)
        self.children_dict: Dict[shogi.AbsoluteCoord, BoardSquare] = {
            x.board_position: x for x in self.children
        }
        self.make_move: bool = False
        self.move_from: shogi.AbsoluteCoord = shogi.NullCoord()
        self.in_check: List[List[shogi.AbsoluteCoord]] = [[], []]

    def space_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Light or make move when a specific space is pressed.

        :param coordinate: location of pressed square
        """
        if not self.make_move or self.move_from == coordinate:
            self.light_moves(coordinate)
        else:
            self.make_moves(self.move_from, coordinate)

    def light_moves(self, coordinate: shogi.AbsoluteCoord):
        """Light up legal moves from a coordinate.

        :param coordinate: coordinate to move from
        """
        pressed_square: BoardSquare = self.children_dict[coordinate]
        pressed_piece: shogi.Piece = self.board[coordinate]
        do_highlight: bool = not pressed_square.is_highlighted
        players_piece: bool = (
                pressed_piece.color == self.board.current_player
        )
        self.un_light_all()
        if do_highlight and players_piece:
            valid_moves = pressed_square.valid_moves(
                self.board,
                self.in_check[pressed_piece.color.int]
            )
            valid_spaces = (
                self.children_dict[x] for x in valid_moves
            )
            for space in valid_spaces:
                space.light()
            if self.board[coordinate]:
                pressed_square.light()
            self.make_move = True
            self.move_from = coordinate
        else:
            self.make_move = False

    def make_moves(
            self,
            current: shogi.AbsoluteCoord,
            to: shogi.AbsoluteCoord
    ):
        """Move piece between two locations.

        :param current: location of piece
        :param to: location to move piece to
        """
        try:
            shogi.move_check_2(self.board, (current, to))
            king_location, checking_own = shogi.check_check(
                self.board,
                (current, to),
                self.board.current_player,
                break_early=True,
                before_move=True
            )
            if checking_own:
                raise shogi.IllegalMove(6)
        except shogi.IllegalMove:
            pass
        else:
            self.board.move(current, to)
            self.update_squares((current, to))
            king_location, is_in_check = shogi.check_check(
                self.board,
                (current, to),
                self.board.current_player.other
            )
            self.in_check[self.board.current_player.other.int] = is_in_check
            self.board.current_player = self.board.current_player.other
            self.make_move = False
            self.un_light_all()

    def update_squares(self, to_update: Iterable[shogi.AbsoluteCoord]):
        """Update specific squares.

        :param to_update: list of squares to update
        """
        for coordinate in to_update:
            space = self.children_dict[coordinate]
            space.text = space.set_string(self.board[coordinate])

    def get_piece(self, position: shogi.AbsoluteCoord) -> shogi.Piece:
        """Get piece at location.

        :param position: position to get piece at
        :return: piece at location
        """
        return self.board[position]

    def un_light_all(self):
        """Un-highlight all squares."""
        highlighted_spaces = {
            x: y for x, y in self.children_dict.items() if y.is_highlighted
        }
        for space in highlighted_spaces.values():
            space.un_light()


class BoardSquare(Button):
    """The class for a board square.

    :ivar board_position: position within board
    :ivar is_highlighted: whether ot not piece is highlighted
    """
    def __init__(
            self,
            position: shogi.AbsoluteCoord,
            initial_occupant: shogi.Piece,
            **kwargs
    ):
        """Initialise instance of BoardSquare.

        :param position: location of square on board
        :param kwargs: standard kwargs for kivy.Button
        """
        self.board_position: shogi.AbsoluteCoord = position
        self.is_highlighted: bool = False
        super().__init__(**kwargs)
        self.text = str(initial_occupant) if initial_occupant else ''

    def light(self):
        """Highlight self."""
        self.background_normal = "./images/Highlighted space.jpg"
        self.background_down = "./images/Highlighted space.jpg"
        self.color = 0, 0, 0, 1
        self.is_highlighted = True

    def un_light(self):
        """Un-highlight self."""
        self.background_normal = "./images/Light square.jpg"
        self.background_down = "./images/Light square.jpg"
        self.color = 1, 1, 1, 1
        self.is_highlighted = False

    @staticmethod
    def set_string(piece: shogi.Piece) -> str:
        """Get string of a piece.

        Mostly a placeholder for now for images later.

        :param piece: piece to get string of.
        :return: string of piece
        """
        return str(piece) if piece else ''

    def valid_moves(
            self,
            current_board: shogi.Board,
            checking_spaces: List[shogi.AbsoluteCoord]
    ) -> List[shogi.AbsoluteCoord]:
        """Get valid moves for square, given current board.

        :param current_board:
        :param checking_spaces:
        :return:
        """
        current_piece = current_board[self.board_position]
        valid_spaces = []
        for dir_number in range(8):
            direction = shogi.Direction(dir_number)
            direction_spaces = current_piece.valid_spaces(direction)
            direction_spaces = shogi.test_spaces(
                current_board,
                self.board_position,
                direction_spaces,
                checking_spaces=checking_spaces
            )
            valid_spaces += direction_spaces
        return valid_spaces


class ShogiBoard(App):
    def build(self):
        return AppCore()


if __name__ == "__main__":
    ShogiBoard().run()
