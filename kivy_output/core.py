from kivy.uix.widget import Widget

from .boardsquare import BoardSquare

import shogi

__all__ = [
    "AppCore"
]


class AppCore(Widget):
    def __init__(self, **kwargs):
        self.board = shogi.Board()
        super().__init__(**kwargs)
        self.captured_spaces = {0: self.ids['0'], 1: self.ids['1']}
        self.make_move = False
        self.move_from = shogi.NullCoord()
        self.in_check = [[], []]

    def update_captured(self, current_board):
        for x, val in enumerate(self.captured_spaces.values()):
            val.update(current_board, shogi.Color(x))

    def update_board(self, squares):
        self.main_board.update_squares(squares)

    def captured_press(self, piece, is_highlighted):
        if not is_highlighted:
            self.main_board.in_play_light(piece)
        else:
            self.un_light_all()
            self.make_move = False

    def un_light_captured(self):
        for x in self.captured_spaces.values():
            x.un_light_all()

    def un_light_board(self):
        self.main_board.un_light_all()

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
            # TODO: Move checking_own into move_check_2
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
            # TODO: Separate out into functions
            is_a_capture = bool(self.board[to])
            self.board.move(current, to)
            self.main_board.update_squares((current, to))
            king_location, is_in_check = shogi.check_check(
                self.board,
                (current, to),
                self.board.current_player.other
            )
            if is_in_check:
                mate = shogi.mate_check(self.board, king_location, is_in_check)
            else:
                mate = False
            if mate:
                pass
            self.in_check[self.board.current_player.other.int] = is_in_check
            self.board.current_player = self.board.current_player.other
            self.make_move = False
            self.un_light_all()
            if is_a_capture:
                self.update_captured(self.board)

    def light_moves(self, coordinate: shogi.AbsoluteCoord):
        """Light up legal moves from a coordinate.

        :param coordinate: coordinate to move from
        """
        pressed_square: BoardSquare = self.main_board.children_dict[coordinate]
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
                self.main_board.children_dict[x] for x in valid_moves
            )
            for space in valid_spaces:
                space.light()
            if self.board[coordinate]:
                pressed_square.light()
            self.make_move = True
            self.move_from = coordinate
        else:
            self.make_move = False

    def un_light_all(self):
        for x in self.ids.values():
            x.un_light_all()

    def in_play_light(self, piece):
        self.un_light_all()
        board_spaces = self.board_spaces.items()
        empty_children = {
            x: y for x, y in board_spaces if not y.occupant
        }
        if piece.color == self.board.current_player:
            for space, x in empty_children.items():
                promotion_zones = ((0, 1, 2), (8, 7, 6))
                player_int = int(piece.color)
                try:
                    index = promotion_zones[player_int].index(space.y)
                except ValueError:
                    x.light()
                else:
                    if index >= piece.auto_promote:
                        x.light()
            self.parent.make_move = True

    @property
    def main_board(self):
        return self.ids['board']

    @property
    def board_spaces(self):
        return self.main_board.children_dict
