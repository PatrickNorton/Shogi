from collections import deque
from typing import Dict, List, Optional, Deque

from kivy.clock import Clock
from kivy.uix.widget import Widget

import shogi
from .boardsquare import BoardSquare
from .capturedsquare import CapturedSquare
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
    :ivar game_log: log of current game
    """

    def __init__(self, **kwargs):
        """Initialise instance of AppCore.

        :param kwargs: keyword arguments to pass
        """
        self.board: shogi.Board = shogi.Board()
        super().__init__(**kwargs)
        self.captured_spaces: Dict[shogi.Color, Widget] = {}
        self.main_board = None
        self.board_spaces = None
        self.make_move: bool = False
        self.move_from: shogi.AbsoluteCoord = shogi.NullCoord()
        self.in_check: Dict[shogi.Color, shogi.CoordSet] = {
            shogi.Color(0): set(),
            shogi.Color(1): set()
        }
        self.to_add: shogi.Piece = shogi.NoPiece()
        self.to_promote: Optional[bool] = None
        self.game_log: List[List[shogi.Move]] = []
        self.undone_moves: Deque[shogi.Move] = deque()
        self.popup_open: bool = False
        Clock.schedule_once(self._set_id_based, 0)

    def make_moves(
            self,
            current: shogi.AbsoluteCoord,
            to: shogi.AbsoluteCoord,
            clear_undone: bool = False
    ):
        """Moves piece between two locations.

        This function first checks that the move is valid, and then
        opens a popup window if it is necessary.
        It also handles promotion opportunities, but check/checkmate
        handling and the actual relocation of pieces does not happen
        until it calls the cleanup() function.

        :param current: location of piece
        :param to: location to move piece to
        :param clear_undone: whether to clear undone moves or not
        """
        move = (current, to)
        checking_spaces = (
            x for x in self.in_check[self.board.current_player] if x != to
        )
        can_move = shogi.check_move(
            self.board,
            move,
            checking_spaces=checking_spaces
        )
        if not can_move:
            return
        captured_piece = self.board[to]
        self.board.move(*move)
        can_promote = self.board.can_promote(to)

        def std_cleanup(*_): self.cleanup(
            move,
            captured_piece=captured_piece,
            clear_undone=clear_undone
        )

        if can_promote and not self.board[to].prom:
            if self.board.auto_promote(to):
                self.to_promote = True
                std_cleanup()
            else:
                pops = PromotionWindow(caller=self)
                pops.bind(on_dismiss=std_cleanup)
                self.popup_open = True
                pops.open()
        else:
            std_cleanup()

    def cleanup(
            self,
            move: shogi.OptCoordTuple,
            captured_piece: shogi.Piece = None,
            dropped_piece: shogi.Piece = None,
            clear_undone: bool = True,
            update_game_log: bool = True,
    ):
        """Cleanup operations for a piece move.

        This function is called as a byproduct of make_moves.
        It runs all of the post-move cleanup, and the check and mate
        validation.
        It modifies the state of the application, and so it probably
        should not be called by itself without good cause.

        :param move: from, to of move
        :param captured_piece: piece captured (None if no capture)
        :param dropped_piece: piece to be dropped, if it is a drop
        :param clear_undone: if the undone moves should be cleared
        :param update_game_log: if game log should be updated
        """
        self.popup_open = False
        current, to = move
        is_a_capture = bool(captured_piece)
        if self.to_promote:
            self.board.promote(to)
        king_location, is_in_check = shogi.is_check(
            self.board,
            move,
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
        else:
            mate = False
        self.in_check[self.board.other_player] = is_in_check
        if update_game_log:
            self.update_game_log(
                move,
                is_a_capture=is_a_capture,
                captured_piece=captured_piece,
                is_a_promote=self.to_promote,
                is_a_drop=(dropped_piece is not None),
                is_mate=(mate if is_in_check else None)
            )
        if clear_undone:
            self.undone_moves.clear()
        self.board.flip_turn()
        self.make_move = False
        self.move_from = shogi.NullCoord()
        self.to_add = None
        self.to_promote = None
        self.un_light_all()
        self.update_board(*move)
        if is_a_capture:
            self.update_captured(self.board)

    def drop_piece(self, space_to: shogi.AbsoluteCoord):
        """Put a specific piece in play.

        :param space_to: space to drop piece at
        """
        can_drop = shogi.is_legal_drop(self.board, self.to_add, space_to)
        if can_drop:
            self.board.put_in_play(self.to_add, space_to)
            self.update_board(space_to)
            self.update_captured(self.board)
            self.cleanup((None, space_to), dropped_piece=self.to_add)

    def undo_last_move(self):
        """Undo the last move made."""
        if not self.game_log:
            return
        last_move = self.game_log[-1].pop()
        if not self.game_log[-1]:
            self.game_log.pop()
        if last_move.is_drop:
            self.board.un_drop(last_move.end)
            if last_move.is_capture:
                self.board.put_in_play(
                    last_move.captured_piece.flip_sides(), last_move.end)
        else:
            self.board.move(last_move.end, last_move.start)
            if last_move.is_capture:
                in_play = last_move.captured_piece.flip_sides()
                if in_play.prom:
                    in_play = in_play.demote()
                self.board.put_in_play(
                    in_play,
                    last_move.end,
                    player=last_move.captured_piece.color.other,
                    flip_sides=True
                )
                if last_move.captured_piece.prom:
                    self.board.promote(last_move.end)
        if last_move.is_promote:
            self.board.demote(last_move.start)
        if self.game_log:
            earlier_move = self.game_log[-1][-1]
            self.cleanup(
                earlier_move.tuple,
                captured_piece=earlier_move.captured_piece,
                dropped_piece=(earlier_move.piece
                               if earlier_move.is_drop
                               else None),
                clear_undone=False,
                update_game_log=False
            )
        self.undone_moves.append(last_move)
        self.update_board(*last_move)
        self.update_captured(self.board)
        self.parent.ids['moves'].remove_last()
        self.board.current_player = last_move.player_color

    def redo_last_move(self):
        """Redo the last move undone."""
        try:
            last_move = self.undone_moves.pop()
        except IndexError:
            return
        if last_move.is_drop:
            self.to_add = last_move.piece
            self.drop_piece(last_move.end)
        else:
            self.make_moves(last_move.start, last_move.end, clear_undone=False)
        self.board.current_player = last_move.player_color.other

    # Lighting methods
    def light_moves(self, coordinate: shogi.AbsoluteCoord):
        """Light up legal moves from a coordinate.

        As a consequence of this function being called, make_moves
        is set, corresponding to whether or not the next press should
        move the piece or not.

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
            valid_spaces = (self.board_spaces[x] for x in valid_moves)
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
        for x in ('board', '0', '1'):
            self.parent.ids[x].un_light_all()

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
        if piece.is_color(self.board.current_player):
            self.un_light_all()
            board_spaces = self.board_spaces.items()
            empty_children = {x: y for x, y in board_spaces if not y.text}
            for space, x in empty_children.items():
                can_drop = shogi.is_legal_drop(self.board, piece, space)
                if can_drop:
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
            captured_piece: shogi.Piece = None,
            is_a_promote: Optional[bool] = None,
            is_a_drop: bool = False,
            is_mate: Optional[bool] = None
    ):
        """Update the game log to add new move.

        :param move: move made
        :param is_a_capture: if the move involved a capture
        :param captured_piece: piece captured
        :param is_a_promote: if the move involved a promotion
        :param is_a_drop: if the move was a drop
        :param is_mate: if move is mate (None if not check)
        """
        if not self.game_log or len(self.game_log[-1]) == 2:
            self.game_log.append([])
        to_log = shogi.Move(
            self.board,
            move,
            is_drop=is_a_drop,
            is_capture=is_a_capture,
            captured_piece=captured_piece,
            is_promote=is_a_promote,
            is_checking=(is_mate is not None),
            is_mate=is_mate
        )
        self.game_log[-1].append(to_log)
        self.parent.ids['moves'].add_move(to_log)

    # Child pressed methods
    def captured_press(self, square: CapturedSquare):
        """One of the captured grids was clicked.

        :param square: square pressed
        """
        if not square.occupant.is_color(self.board.current_player):
            return
        piece = square.occupant
        is_highlighted = square.is_highlighted
        if not self.make_move:
            if is_highlighted:
                raise RuntimeError("make_move should not be false & space lit")
            else:
                self.in_play_light(piece)
                self.to_add = piece
                square.light()
        else:
            if is_highlighted:
                self.un_light_all()
                self.make_move = False

    def board_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Board was clicked.

        :param coordinate: where board was clicked
        """
        if self.make_move and coordinate != self.move_from:
            if self.to_add:
                self.drop_piece(coordinate)
            else:
                self.make_moves(self.move_from, coordinate)
        else:
            self.light_moves(coordinate)

    def text_entered(self, text: str):
        """Text was entered from text box.

        :param text: text entered
        """
        try:
            coordinate = shogi.AbsoluteCoord(text)
        except ValueError:
            return
        self.board_pressed(coordinate)

    def _set_id_based(self, _):
        """Set id based variables.

        This needs to exist, as self.parent.ids is not accessible during
        __init__, but this should still be created then. **DO NOT USE
        OUTSIDE OF __init__!!**
        """
        self.captured_spaces = {
            shogi.Color(0): self.parent.ids['0'],
            shogi.Color(1): self.parent.ids['1']
        }
        self.main_board = self.parent.ids['board']
        self.board_spaces = self.main_board.children_dict
