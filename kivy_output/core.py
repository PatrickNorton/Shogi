from collections import deque
from typing import Dict, List, Optional, Deque

from kivy.clock import Clock
from kivy.uix.widget import Widget

import shogi
from .boardsquare import BoardSquare
from .capturedsquare import CapturedSquare
from .gamestate import GameState
from .inputs import MateWindow, PromotionWindow

__all__ = [
    "AppCore",
]


class AppCore(Widget):
    """Core of app. Contains all necessary functions for the game.

    :ivar board: master board
    :ivar captured_spaces: index of CapturedGrids for each color
    :ivar main_board: Kivy widget representing the main board
    :ivar board_spaces: Dict of coords to each Kivy board space
    :ivar game_state: Object representing the state of the game
    :ivar game_log: log of current game
    :ivar undone_moves: log of moves that have been undone
    :ivar popup_open: whether or not the promotion popup is open
    """

    def __init__(self, **kwargs):
        """Initialise instance of AppCore.

        :param kwargs: keyword arguments to pass
        """
        # Board: current state
        self.board: shogi.Board = shogi.Board()
        super().__init__(**kwargs)
        self.game_state = GameState()
        self.game_log: List[List[shogi.Move]] = []
        self.undone_moves: Deque[shogi.Move] = deque()
        self.popup_open: bool = False
        # Vars set in _set_id_based:
        self.captured_spaces: Dict[shogi.Color, Widget] = {}
        self.main_board: shogi.Board = None
        self.board_spaces: Dict[shogi.AbsoluteCoord, BoardSquare] = {}
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
            x for x in self.game_state.in_check[self.board.current_player]
            if x != to
        )
        if not shogi.check_move(  # Is the move actually legal?
            self.board,
            move,
            checking_spaces=checking_spaces
        ):
            return   # If not legal, end there before anything happens
        captured_piece = self.board[to]
        self.board.move(*move)
        can_promote = self.board.can_promote(to)

        # Standard cleanup call, needed b/c execution continues when a
        # popup window is opened, for some reason
        def std_cleanup(*_): self.cleanup(
            move,
            captured_piece=captured_piece,
            clear_undone=clear_undone
        )

        # Handle promotion and call cleanup function
        if can_promote and not self.board[to].prom:
            if self.board.auto_promote(to):
                self.game_state.to_promote = True
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
        if self.game_state.to_promote:
            self.board.promote(to)
        is_in_check = shogi.is_check(
            self.board,
            move,
            self.board.other_player,
            dropped_piece=dropped_piece
        )
        # Run mate stuff, if there is a check
        if is_in_check:
            mate = shogi.mate_check(
                self.board,
                is_in_check
            )
            if mate:
                pops = MateWindow()
                pops.open()
                # TODO: run EOG when checkmate happens
        else:
            mate = False
        # Update the spaces attacking the king
        self.game_state.in_check[self.board.other_player] = is_in_check
        # Update the game log, but only if permitted
        # Not called when undoing a move, for example
        if update_game_log:
            self.update_game_log(
                move,
                is_a_capture=is_a_capture,
                captured_piece=captured_piece,
                is_a_promote=self.game_state.to_promote,
                is_a_drop=(dropped_piece is not None),
                is_mate=(mate if is_in_check else None)
            )
        # Clear the undone moves log (prevents weird breakage with
        # redoing into a weird state)
        # Not called when undoing or redoing a move, e.g.
        if clear_undone:
            self.undone_moves.clear()
        # Reset all of the game-state variables back to their pre-
        # move states, ready for the next turn
        self.board.flip_turn()
        self.game_state.post_turn()
        self.un_light_all()
        # Update the display so the player can see all the hard work
        # this computer has done
        self.update_board(*move)
        if is_a_capture:
            self.update_captured(self.board)

    def drop_piece(self, space_to: shogi.AbsoluteCoord):
        """Put a specific piece in play.

        :param space_to: space to drop piece at
        """
        if shogi.is_legal_drop(self.board, self.game_state.to_add, space_to):
            self.board.put_in_play(self.game_state.to_add, space_to)
            self.update_board(space_to)
            self.update_captured(self.board)
            self.cleanup(
                (None, space_to),
                dropped_piece=self.game_state.to_add
            )

    def undo_last_move(self):
        """Undo the last move made."""

        # If the game log does not exist (e.g. undoing before the
        # first move), don't do anything
        if not self.game_log:
            return
        # Figure out what the last move was, and clear it from the
        # game log, so it doesn't show up
        last_move = self.game_log[-1].pop()
        if not self.game_log[-1]:
            self.game_log.pop()
        # If the last move was a drop, un-drop the piece
        if last_move.is_drop:
            self.board.un_drop(last_move.end)
        # Otherwise, move the piece backwards
        else:
            self.board.move(last_move.end, last_move.start)
            # Undo any capturing, if it happened
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
            # Demote the piece, if it was promoted
            if last_move.is_promote:
                self.board.demote(last_move.start)
        if self.game_log:
            # Fix the game log to reflect the new reality
            earlier_move = self.game_log[-1][-1]
            self.cleanup(
                earlier_move.tuple,
                captured_piece=earlier_move.captured_piece,
                dropped_piece=(earlier_move.piece
                               if earlier_move.is_drop
                               else None),
                clear_undone=False,    # Don't update the game log in
                update_game_log=False  # the cleanup, that'd be bad
            )
        # A little more undo-specific cleanup and window-displaying
        self.undone_moves.append(last_move)
        self.update_board(*last_move)
        self.update_captured(self.board)
        self.parent.ids['moves'].remove_last()
        # Change the turn explicitly, as bad things can happen if
        # you're not careful about this kind of stuff
        self.board.current_player = last_move.player_color

    def redo_last_move(self):
        """Redo the last move undone."""
        # If there's no undone moves, simply return without doing
        # anything. Otherwise, get the last undone move.
        try:
            last_move = self.undone_moves.pop()
        except IndexError:
            return
        if last_move.is_drop:
            # Drop the piece, if it was a drop
            self.game_state.to_add = last_move.piece
            self.drop_piece(last_move.end)
        else:
            # Otherwise, make the move from and to
            self.make_moves(last_move.start, last_move.end, clear_undone=False)
        # Again, explicitly set the turn, just in case
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
        players_piece: bool = pressed_piece.is_color(self.board.current_player)
        # Start by making sure no extraneous spaces are lit
        self.un_light_all()
        # If the pressed square is not highlighted, and it belongs to
        # the player, do the highlighting
        if do_highlight and players_piece:
            # Light up every square it's possible to move to
            for space in pressed_square.valid_moves(
                self.board,
                self.game_state.in_check[pressed_piece.color]
            ):
                self.board_spaces[space].light()
            # Light the pressed square
            pressed_square.light()
            # Set game-state variables to reflect the current state
            self.game_state.make_move = True
            self.game_state.move_from = coordinate
        # Otherwise, un-light all the squares (already done), and shut
        # everything down
        else:
            self.game_state.make_move = False

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

    def drop_light(self, piece: shogi.Piece):
        """Light all squares where a piece could be dropped.

        :param piece: piece to be drop-tested
        """
        # Light squares only if the piece is of the correct color
        if piece.is_color(self.board.current_player):
            # Start with a blank slate
            self.un_light_all()
            # Light every legally-drop-able space
            for space, x in self.board_spaces.items():
                if shogi.is_legal_drop(self.board, piece, space):
                    x.light()
            # Set game-state variables to reflect the new developments
            self.game_state.make_move = True

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
        # Add a new pair of turns if the last one is full
        if not self.game_log or len(self.game_log[-1]) == 2:
            self.game_log.append([])
        # Create the Move object to be added to the logs
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
        # Add the object to the move log and the widget on the board
        self.game_log[-1].append(to_log)
        self.parent.ids['moves'].add_move(to_log)

    # Child pressed methods
    def captured_press(self, square: CapturedSquare):
        """One of the captured grids was clicked.

        :param square: square pressed
        """
        # If the square is not occupied, ignore it
        if not square.occupant.is_color(self.board.current_player):
            return
        # If this click is not the second in a move-set:
        if not self.game_state.make_move:
            # If the square is already highlighted, something has gone
            # badly wrong. Fail accordingly.
            if square.is_highlighted:
                raise RuntimeError("make_move should not be false & space lit")
            # Otherwise, continue upon your merry way
            else:
                # Highlight and set move-state variables
                self.drop_light(square.occupant)
                self.game_state.to_add = square.occupant
                square.light()
        else:
            # If the square is highlighted, un-light everything
            # Otherwise, do nothing
            if square.is_highlighted:
                self.un_light_all()
                self.game_state.make_move = False

    def board_pressed(self, coordinate: shogi.AbsoluteCoord):
        """Board was clicked.

        :param coordinate: where board was clicked
        """
        # If this is the click marking where to move:
        if (self.game_state.make_move
                and coordinate != self.game_state.move_from):
            # If there is a piece to drop, drop it
            if self.game_state.to_add:
                self.drop_piece(coordinate)
            # Otherwise, move the piece where it needs to go
            else:
                self.make_moves(self.game_state.move_from, coordinate)
        # Otherwise, light the possible move options
        else:
            self.light_moves(coordinate)

    def text_entered(self, text: str):
        """Text was entered from text box.

        :param text: text entered
        """
        # If text makes a valid coordinate, pretend it was clicked.
        # Otherwise, do nothing
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
        self.main_board.set_up_squares()
        self.board_spaces = self.main_board.children_dict
