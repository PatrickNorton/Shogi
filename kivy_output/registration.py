from kivy.factory import Factory

from .boardsquare import BoardSquare
from .boardwidget import ChessBoard
from .captured import CapturedGrid
from .capturedsquare import CapturedSquare
from .core import AppCore
from .inputs import HelpRst, PromotionWindow, MateWindow, HelpText
from .movetable import MoveGrid, MoveBox
from .numbers import NumberLayout, NumButton
from .screens import HelpScreen, MainScreen


def register_classes():
    """Register all classes to Kivy.

    This is necessary for kivy to function.
    It should be done automatically (I think), but it seems not to
    work, so instead I have added this.
    It registers to kivy every class currently defined.
    """
    for cls in (BoardSquare, ChessBoard, CapturedGrid, CapturedSquare,
                AppCore, HelpRst, PromotionWindow, MateWindow, HelpText,
                NumberLayout, HelpScreen, MainScreen, MoveGrid, MoveBox,
                NumButton):
        Factory.register(cls.__name__, cls=cls)
