from typing import Iterable, Generator

from kivy.uix.button import Button

import shogi

__all__ = [
    "BoardSquare",
]


class BoardSquare(Button):
    """The class for a board square.

    :ivar board_position: position within board
    :ivar is_highlighted: whether or not piece is highlighted
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
        # The position of the space within the board at large
        self.board_position: shogi.AbsoluteCoord = position
        # Whether or not the space is highlighted
        self.is_highlighted: bool = False
        super().__init__(**kwargs)
        # The text on the space, telling who occupies it
        self.text = str(initial_occupant) if initial_occupant else ''

    def light(self):
        """Highlight self."""
        self.background_normal = "Highlighted space.jpg"
        self.background_down = "Highlighted space.jpg"
        self.color = 0, 0, 0, 1
        self.is_highlighted = True

    def un_light(self):
        """Un-highlight self."""
        self.background_normal = "Light square.jpg"
        self.background_down = "Light square.jpg"
        self.color = 1, 1, 1, 1
        self.is_highlighted = False

    @staticmethod
    def set_string(piece: shogi.Piece) -> str:
        """Get string of a piece.

        Mostly a placeholder for now for images later.
        This will be used for the setting of images when I get around
        to it.

        :param piece: piece to get string of.
        :return: string of piece
        """
        return str(piece) if piece else ''

    def valid_moves(
            self,
            current_board: shogi.Board,
            checking_spaces: Iterable[shogi.AbsoluteCoord]
    ) -> Generator:
        """Get valid moves for square, given current board.

        This function takes an iterable of spaces checking the king
        and the current board state in order to produce the set of
        spaces to which it may travel.

        :param current_board: current board position
        :param checking_spaces: spaces checking king
        :return: set of valid spaces
        """
        current_piece = current_board[self.board_position]
        for direction in shogi.Direction.valid():
            # Get the valid spaces in each direction and yield each
            yield from shogi.test_spaces(
                current_board,
                self.board_position,
                current_piece.valid_spaces(direction),
                checking_spaces=checking_spaces
            )
