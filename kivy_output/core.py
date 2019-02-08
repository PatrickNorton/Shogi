from typing import Dict, List, Optional

from kivy.clock import Clock
from kivy.uix.widget import Widget

import shogi
from .boardsquare import BoardSquare
from .inputs import MateWindow, PromotionWindow

__all__ = [
    "AppCore",
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

    def __init__(self, **kwargs):
        """Initialise instance of AppCore.

        :param kwargs: keyword arguments to pass
        """
        self.board = shogi.Board()
        super().__init__(**kwargs)
        self.captured_spaces: Dict[shogi.Color, Widget] = {}
        self.make_move: bool = False
        self.move_from: shogi.AbsoluteCoord = shogi.NullCoord()
        self.in_check: Dict[shogi.Color, shogi.CoordSet] = {
            shogi.Color(0): set(),
            shogi.Color(1): set()
        }
        self.to_add: shogi.Piece = shogi.NoPiece()
        self.to_promote: bool = None
        self.game_log: List[List[str]] = []
        Clock.schedule_once(self._set_captured, 0)

    def make_moves(
            self,
            current: shogi.AbsoluteCoord,
            to: shogi.AbsoluteCoord
    ):
        """Move piece between two locations.

        :param current: location of piece
        :param to: location to move piece to
        """
        checking_spaces = [
            x for x in self.in_check[self.board.current_player] if x != to
        ]
        cannot_move = shogi.check_move(
            self.board,
            (current, to),
            checking_spaces=checking_spaces
        )
        if cannot_move:
            return
        is_a_capture = bool(self.board[to])
        self.board.move(current, to)
        self.update_board(current, to)
        can_promote = self.board.can_promote(to)
        if can_promote and not self.board[to].prom:
            if self.board.auto_promote(to):
                self.to_promote = True
                self.cleanup((current, to), is_a_capture=is_a_capture)
            else:
                pops = PromotionWindow(caller=self)
                pops.bind(
                    on_dismiss=lambda x: self.cleanup(
                        (current, to),
                        is_a_capture=is_a_capture
                    )
                )
                pops.open()
        else:
            self.cleanup((current, to), is_a_capture=is_a_capture)

    def cleanup(
            self,
            move: shogi.OptCoordTuple,
            is_a_capture: bool = False,
            dropped_piece: shogi.Piece = None
    ):
        """Cleanup operations for a piece move.

        :param move: from, to of move
        :param is_a_capture: if the move involved a capture
        :param dropped_piece: piece to be dropped, if it is a drop
        """
        current, to = move
        is_a_promote = self.to_promote
        if self.to_promote:
            self.board.promote(to)
            self.update_board(to)
            self.to_promote = None
        king_location, is_in_check = shogi.check_check(
            self.board,
            (current, to),
            self.board.other_player,
            dropped_piece=dropped_piece
        )
        if is_in_check:
            mate = shogi.mate_check(
                self.board,
                king_location,
                is_in_check
            )
            if mate:
                pops = MateWindow()
                pops.open()
                # TODO: run EOG when checkmate happens
        self.in_check[self.board.other_player] = is_in_check
        self.update_game_log(
            move,
            is_a_capture=is_a_capture,
            is_a_promote=is_a_promote,
            is_a_drop=(dropped_piece is not None)
        )
        self.board.flip_turn()
        self.make_move = False
        self.move_from = shogi.NullCoord()
        self.to_add = None
        self.un_light_all()
        if is_a_capture:
            self.update_captured(self.board)

    def drop_piece(self, space_to: shogi.AbsoluteCoord):
        """Put a specific piece in play.

        :param space_to: space to drop piece at
        """
        cannot_drop = shogi.drop_check(
            self.board,
            self.to_add,
            space_to
        )
        if not cannot_drop:
            self.board.put_in_play(self.to_add, space_to)
            self.update_board(space_to)
            self.update_captured(self.board)
            self.cleanup((None, space_to), dropped_piece=self.to_add)

    # Lighting methods
    def light_moves(self, coordinate: shogi.AbsoluteCoord):
        """Light up legal moves from a coordinate.

        :param coordinate: coordinate to move from
        """
        pressed_square: BoardSquare = self.board_spaces[coordinate]
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
                self.board_spaces[x] for x in valid_moves
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
        values = (
            y for x, y in self.parent.ids.items() if x not in ('core', 'moves')
        )
        for x in values:
            x.un_light_all()

    def un_light_captured(self):
        """Un-light all captured squares."""
        for x in self.captured_spaces.values():
            x.un_light_all()

    def un_light_board(self):
        """Un-light entire board."""
        self.main_board.un_light_all()

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
                cannot_drop = shogi.drop_check(
                    self.board,
                    piece,
                    space
                )
                if not cannot_drop:
                    x.light()
            self.make_move = True

    # Updating methods
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

    def update_game_log(
            self,
            move: shogi.OptCoordTuple,
            is_a_capture: bool = False,
            is_a_promote: Optional[bool] = None,
            is_a_drop: bool = False
    ):
        """Update the game log to add new move.

        :param move: move made
        :param is_a_capture: if the move involved a capture
        :param is_a_promote: if the move involved a promotion
        :param is_a_drop: if the move was a drop
        """
        if not self.game_log or len(self.game_log[-1]) == 2:
            self.game_log.append([])
        to_log = shogi.to_notation(
            self.board,
            move,
            is_drop=is_a_drop,
            is_capture=is_a_capture,
            is_promote=is_a_promote
        )
        self.game_log[-1].append(to_log)
        self.parent.ids['moves'].add_move(to_log)

    # Child pressed methods
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

    def board_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Board was clicked.

        :param coordinate: where board was clicked
        """
        if self.make_move and coordinate != self.move_from:
            if self.move_from:
                self.make_moves(self.move_from, coordinate)
            else:
                self.drop_piece(coordinate)
        else:
            self.light_moves(coordinate)

    def _set_captured(self, _):
        """Set captured_spaces method.

        This needs to exist, as self.parent.ids is not accessible during
        __init__, but this should still be created then. DO NOT USE
        OUTSIDE OF __init__!!
        """
        self.captured_spaces = {
            shogi.Color(0): self.parent.ids['0'],
            shogi.Color(1): self.parent.ids['1']
        }

    @property
    def main_board(self):
        return self.parent.ids['board']

    @property
    def board_spaces(self) -> dict:
        return self.main_board.children_dict
