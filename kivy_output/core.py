from kivy.uix.widget import Widget
from kivy.clock import Clock

from .app import PromotionWindow
from .boardsquare import BoardSquare

import shogi

__all__ = [
    "AppCore"
]


class AppCore(Widget):
    """Core of app. Contains all necessary functions for the game.

    :ivar board: master board
    :ivar captured_spaces: index of CapturedGrids for each color
    :ivar make_move: whether next click makes a move or highlights
    :ivar move_from: where the piece is moving from
    :ivar in_check: pieces attacking king for each color
    :ivar to_add: piece to add to board
    """
    # TODO: Change to not use make_move, but move_from or to_add instead
    def __init__(self, **kwargs):
        """Initialise instance of AppCore.

        :param kwargs: keyword arguments to pass
        """
        self.board = shogi.Board()
        super().__init__(**kwargs)
        self.captured_spaces = {}
        self.make_move = False
        self.move_from = shogi.NullCoord()
        self.in_check = {
            shogi.Color(0): [],
            shogi.Color(1): []
        }
        self.to_add = shogi.NoPiece()
        Clock.schedule_once(self._set_captured, 0)

    def update_captured(self, current_board: shogi.Board):
        """Update captured squares.

        :param current_board: current board state
        """
        for x, val in enumerate(self.captured_spaces.values()):
            val.update(current_board, shogi.Color(x))

    def update_board(self, *squares: BoardSquare):
        """Update specific squares on board.

        :param squares: squares to update
        """
        self.main_board.update_squares(*squares)

    def captured_press(self, piece: shogi.Piece, is_highlighted: bool):
        """One of the captured grids was clicked.

        :param piece: piece clicked
        :param is_highlighted: if square clicked is highlighted
        """
        if not is_highlighted:
            self.in_play_light(piece)
            self.to_add = piece
        else:
            self.un_light_all()
            self.make_move = False

    def un_light_captured(self):
        """Un-light all captured squares."""
        for x in self.captured_spaces.values():
            x.un_light_all()

    def un_light_board(self):
        """Un-light entire board."""
        self.main_board.un_light_all()

    def board_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Board was clicked.

        :param coordinate: where board was clicked
        """
        if self.make_move and coordinate != self.move_from:
            if self.move_from:
                self.make_moves(self.move_from, coordinate)
            else:
                self.put_in_play(coordinate)
        else:
            self.light_moves(coordinate)

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
            self.main_board.update_squares(current, to)
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
            can_promote = self.board.can_promote(to)

            if can_promote and not self.board[to].prom:
                if self.board.auto_promote(to):
                    self.board.promote(to)
                    self.update_board(to)
                else:
                    pops = PromotionWindow(to_highlight=to, caller=self)
                    pops.open()
            self.in_check[self.board.current_player.other] = is_in_check
            self.board.current_player = self.board.current_player.other
            self.make_move = False
            self.move_from = shogi.NullCoord()
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
                self.in_check[pressed_piece.color]
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
        """Un-light all squares."""
        for x in self.ids.values():
            x.un_light_all()

    def in_play_light(self, piece: shogi.Piece):
        """Light all squares where a piece could be dropped.

        :param piece: piece to be drop-tested
        """
        self.un_light_all()
        board_spaces = self.board_spaces.items()
        empty_children = {
            x: y for x, y in board_spaces if not y.text
        }
        if piece.color == self.board.current_player:
            for space, x in empty_children.items():
                try:
                    shogi.drop_check(
                        self.board,
                        piece,
                        space
                    )
                except shogi.IllegalMove:
                    pass
                else:
                    x.light()
            self.make_move = True

    def put_in_play(self, space_to: shogi.AbsoluteCoord):
        """Put a specific piece in play.

        :param space_to: space to drop piece at
        """
        promotion_zones = ((0, 1, 2), (8, 7, 6))
        player_int = int(self.to_add.color)
        try:
            index = promotion_zones[player_int].index(space_to.y)
        except ValueError:
            put_in_play = True
        else:
            put_in_play = (index >= self.to_add.auto_promote)
        if put_in_play:
            self.board.put_in_play(self.to_add, space_to)
            self.update_board(space_to)
            self.update_captured(self.board)
            self.un_light_all()
            self.board.current_player = self.board.current_player.other

    def _set_captured(self, _):
        self.captured_spaces = {
            shogi.Color(0): self.ids['0'],
            shogi.Color(1): self.ids['1']
        }

    @property
    def main_board(self):
        return self.ids['board']

    @property
    def board_spaces(self):
        return self.main_board.children_dict