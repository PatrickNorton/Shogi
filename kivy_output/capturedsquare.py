from kivy.uix.button import Button

import shogi

__all__ = [
    "CapturedSquare"
]


class CapturedSquare(Button):
    """The squares that hold the captured pieces.

    :ivar occupant: occupant of the square
    :ivar position: position within grid
    """
    def __init__(self, position: int, **kwargs):
        """Initialise instance of CapturedSquare.

        :param kwargs: keyword arguments to be sent
        """
        self.occupant: shogi.Piece = shogi.NoPiece()
        self.position: int = position
        self.is_highlighted = False
        super().__init__(**kwargs)

    def give_piece(self, piece: shogi.Piece):
        """Add an occupying piece to the square.

        :param piece: piece to be added
        """
        self.background_color = 1, 1, 1, 1
        self.text = str(piece)
        self.occupant = piece

    def remove_piece(self):
        """Remove occupying piece from square."""
        self.background_color = 0, 0, 0, 0
        self.text = ''
        self.occupant = shogi.NoPiece()

    def on_press(self):
        """Captured square was pressed."""
        if self.occupant:
            if self.is_highlighted:
                self.un_light()
                self.parent.parent.un_light_all()
            elif not self.parent.parent.make_move:
                self.parent.space_pressed(self.position, self.is_highlighted)
                if self.parent.parent.make_move:
                    self.light()

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
