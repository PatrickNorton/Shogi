from kivy.uix.gridlayout import GridLayout

from typing import Dict, List, Iterable

import shogi

from .boardsquare import BoardSquare


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
            is_a_capture = bool(self.board[to])
            self.board.move(current, to)
            self.update_squares((current, to))
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
                self.parent.update_captured(self.board)

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
        self.parent.un_light_captured()
        highlighted_spaces = {
            x: y for x, y in self.children_dict.items() if y.is_highlighted
        }
        for space in highlighted_spaces.values():
            space.un_light()
        self.make_move = False

    def in_play_light(self, piece):
        self.un_light_all()
        empty_children = {
            x: y for x, y in self.children_dict.items() if not y.text
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
        self.make_move = True
