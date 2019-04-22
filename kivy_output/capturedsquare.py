from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.button import Button

import shogi

__all__ = [
    "CapturedSquare",
]


class CapturedSquare(Button):
    """The squares that hold the captured pieces.

    :ivar occupant: occupant of the square
    :ivar position: position within grid
    """

    # Space's position in the grid of spaces
    position = NumericProperty(None)
    # Whether or not the space is highlighted
    is_highlighted = BooleanProperty(False)
    # The occupant of the space
    occupant = ObjectProperty(shogi.NoPiece())

    def __init__(self, position: int, **kwargs):
        """Initialise instance of CapturedSquare.

        :param kwargs: keyword arguments to be sent
        """
        super().__init__(position=position, is_highlighted=False, **kwargs)

    def give_piece(self, piece: shogi.Piece):
        """Add an occupying piece to the square.

        TODO? Use property for this instead

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
            self.parent.space_pressed(self.position)

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
