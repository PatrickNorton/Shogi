from kivy.factory import Factory

from .boardsquare import BoardSquare
from .boardwidget import ChessBoard
from .captured import CapturedGrid
from .capturedsquare import CapturedSquare
from .core import AppCore
from .inputs import HelpRst, PromotionWindow, MateWindow, HelpText
from .movetable import MoveGrid, MoveBox
from .numbers import NumberLayout
from .screens import HelpScreen, MainScreen


def register_classes():
    for cls in (BoardSquare, ChessBoard, CapturedGrid, CapturedSquare,
                AppCore, HelpRst, PromotionWindow, MateWindow, HelpText,
                NumberLayout, HelpScreen, MainScreen, MoveGrid, MoveBox):
        Factory.register(cls.__name__, cls=cls)
