from .exceptions import PromotedException, NotPromotableException
from .exceptions import DemotedException
from .locations import Direction, RelativeCoord
from .information import info
from typing import Union, Dict, Optional, Generator
import collections

__all__ = [
    "Color",
    "PieceType",
    "Moves"
]


class Color:
    """The class for piece/player colors.

    This class is used both for the color of a player (e.g. the Board
    object's current_player attribute being an instance of Color),
    and the color of a piece (e.g. the Piece.color attribute being a
    Color). This class is what should be used for comparisons between
    two piece's colors.

    :ivar int: the integer (white=0, black=1) of the turn
    :ivar name: the character (w, b) of the color
    :ivar other_color: the character of the other color
    :ivar full_name: the full name of the color

    """

    def __init__(self, turn_num: Union[int, str, 'Color']):
        """Initialise instance of Color.

        :param turn_num: piece's color (w/b or 0/1)
        :raises TypeError: invalid type
        """

        self.int: int
        self.name: str
        if isinstance(turn_num, int):
            self.int = turn_num
            self.name = 'wb'[self.int]
        elif isinstance(turn_num, str):
            if turn_num == '-':
                self.name = turn_num
                self.int = -1
            else:
                self.name = turn_num
                self.int = 'wb'.index(turn_num)
        elif isinstance(turn_num, Color):
            self.int = turn_num.int
            self.name = 'wb'[self.int]
        else:
            raise TypeError
        self.other_color = 'bw'[self.int]
        self.full_name = ['White', 'Black'][self.int]

    def __str__(self): return self.name

    def __repr__(self): return self.full_name

    def __int__(self): return self.int

    def __eq__(self, other: 'Color'): return self.int == other.int

    def __hash__(self): return hash((self.int, self.name))

    @property
    def other(self) -> 'Color':
        """Color: Opposite color from first"""

        return Color(self.other_color)


class PieceType:
    """The class for the type of the piece.

    This class is what determines which type the piece is (e.g. king,
    rook, knight, etc.). It should be used for comparisons between
    two piece's types.

    :ivar type: the short name of the piece -- see "help names"
    :ivar name: the full name of the piece
    """

    def __init__(self, typ: Union[str, 'PieceType'], promoted: bool = False):
        """Initialise instance of PieceType.

        :param typ: type of piece ('n', 'b', etc.)
        :param promoted: if piece is promoted
        """

        typ = str(typ)
        self.type: str
        self.name: str
        if promoted:
            self.type = typ.lower()
            self.name = f"+{info.name_info[self.type]}"
        else:
            self.type = typ.lower()
            self.name = info.name_info[self.type]

    def __str__(self): return self.type

    def __repr__(self): return self.name

    def __eq__(self, other): return repr(self) == repr(other)

    def __hash__(self): return hash((self.type, self.name))

    def prom(self) -> 'PieceType':
        """Promote the piece."""
        self.type = self.type.upper()
        self.name = '+' + self.name
        return self

    def dem(self) -> 'PieceType':
        """Demote the piece."""
        self.type = self.type.lower()
        self.name = self.name.replace('+', '')
        return self


class Moves(collections.abc.Sequence):
    """The class containing the set of moves the piece can do.

    This class contains a dictionary relating directions to the moves
    the piece can make. It also has the ability to test whether or not
    a certain move can be made.

    :ivar name: 1-letter name of piece
    :ivar color: color of piece
    :ivar demoted: direction -> move when not promoted
    :ivar promoted: direction -> move when promoted
    :ivar moves: (demoted, promoted)
    :ivar is_promoted: if the piece is promoted
    :ivar current: current set of moves
    """

    def __init__(
            self, piece_name: Union[str, PieceType],
            clr: Color,
            promoted: bool = False
    ):
        """Initialise instance of moves.

        :param piece_name: 1-letter name of piece
        :param clr: color of piece
        :param promoted: if piece is promoted
        :raises NotPromotableException: if un-promotable is promoted
        """

        piece_name = str(piece_name)
        move_list = list(info.move_info[piece_name])
        if clr == Color(1):
            for y, var in enumerate(move_list):
                if var is not None:
                    move_list[y] = var[4:]+var[:4]
        move_list = move_list[0]
        self.demoted: Dict[Direction, str]
        self.name: str = piece_name
        self.color: Color = clr
        self.demoted: Dict[Direction, str]
        self.demoted = {Direction(x): move_list[x] for x in range(8)}
        self.demoted[Direction(8)] = '-'
        move_list = move_list[1]
        self.promoted: Optional[Dict[Direction, str]]
        if move_list is None:
            self.promoted = None
        else:
            self.promoted = {Direction(x): move_list[x] for x in range(8)}
            self.promoted[Direction(8)] = '-'
        self.moves: tuple = (self.demoted, self.promoted)
        self.is_promoted: bool = promoted
        self.current: Dict[Direction, str] = self.moves[self.is_promoted]
        if self.current is None:
            raise NotPromotableException

    def __getitem__(self, attr: Union[Direction, int]) -> str:
        if isinstance(attr, Direction):
            return self.current[attr]
        elif isinstance(attr, int):
            return self.current[Direction(attr)]
        else:
            raise TypeError

    def __iter__(self) -> Generator: yield from self.current.values()

    def __len__(self) -> int: return len(self.current)

    def can_move(self, relative_location: RelativeCoord) -> bool:
        """Check if piece can move to location.

        :param relative_location: relative location of move
        :return: if move is legal
        """

        vec = Direction(relative_location)
        dist = max(abs(relative_location))
        magic_var = self[vec]
        if magic_var == '-':
            return False
        elif magic_var == '1':
            return dist == 1
        elif magic_var == '+':
            return True
        elif magic_var == 'T':
            return abs(relative_location) == (1, 2)
        return False

    def prom(self) -> 'Moves':
        """Promote self.

        :raises PromotedException: already promoted
        :return: promoted version of self
        """

        if self.is_promoted:
            raise PromotedException
        return Moves(self.name, self.color, True)

    def dem(self) -> 'Moves':
        """Demote self.

        :raises DemotedException: already demoted
        :return: demoted exception of self
        """

        if not self.is_promoted:
            raise DemotedException
        return Moves(self.name, self.color, False)
