import collections
from typing import Callable, Dict, Generator, Optional, Union

from .exceptions import (
    PromotedException, NotPromotableException, DemotedException
)
from .information import info
from .locations import Direction, RelativeCoord

__all__ = [
    "Color",
    "Rank",
    "Moves",
    "PieceMove",
    "ColorLike",
    "RankLike",
    "MoveFnLike",
]


ColorLike = Union[int, str, 'Color']
RankLike = Union[str, 'Rank']
MoveFnLike = Callable[[RelativeCoord], bool]


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

    def __init__(self, turn_num: ColorLike):
        """Initialise instance of Color.

        :param turn_num: piece's color (w/b or 0/1)
        :raises TypeError: invalid rank
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
        self.other_color: str = 'bw'[self.int]
        self.full_name: str = ['White', 'Black'][self.int]

    def __str__(self): return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}({self.int})"

    def __int__(self): return self.int

    def __eq__(self, other: 'Color'): return self.int == other.int

    def __hash__(self): return hash((self.int, self.name))

    @staticmethod
    def valid() -> Generator['Color', None, None]:
        yield Color(0)
        yield Color(1)

    @property
    def other(self) -> 'Color':
        """Color: Opposite color from first"""

        return Color(self.other_color)


class Rank:
    """The class for the rank of the piece.

    This class is what determines which rank the piece is (e.g. king,
    rook, knight, etc.). It should be used for comparisons between
    two piece's types.

    :ivar rank: the short name of the piece -- see "help names"
    :ivar name: the full name of the piece
    """

    def __init__(self, rank: RankLike, promoted: bool = False):
        """Initialise instance of Rank.

        :param rank: rank of piece ('n', 'b', etc.)
        :param promoted: if piece is promoted
        """

        rank = str(rank)
        self.rank: str
        self.name: str
        if promoted:
            self.rank = rank.upper()
            self.name = f"+{info.name_info[self.rank.lower()]}"
        else:
            self.rank = rank.lower()
            self.name = info.name_info[self.rank]

    def __str__(self): return self.rank

    def __repr__(self):
        # Implicit string concatenation
        return (f"{self.__class__.__name__}"
                f"({self.rank !r}, promoted={self.rank.isupper()})")

    def __eq__(self, other): return self.name == other.name

    def __hash__(self): return hash((self.rank, self.name))

    def prom(self) -> 'Rank':
        """Promote the piece."""
        return Rank(self, promoted=True)

    def dem(self) -> 'Rank':
        """Demote the piece."""
        return Rank(self, promoted=False)


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
            self,
            piece_name: RankLike,
            color: Color,
            promoted: bool = False
    ):
        """Initialise instance of moves.

        :param piece_name: 1-letter name of piece
        :param color: color of piece
        :param promoted: if piece is promoted
        :raises NotPromotableException: if un-promotable is promoted
        """

        piece_name = str(piece_name).lower()
        move_list = list(info.move_info[piece_name])
        if color == Color(1):
            for y, var in enumerate(move_list):
                if var is not None:
                    move_list[y] = var[4:] + var[:4]
        move_demoted = move_list[0]
        self.name: str = piece_name
        self.color: Color = color
        self.demoted: Dict[Direction, str] = {
            d: move_demoted[x] for x, d in enumerate(Direction.valid())
        }
        self.demoted[Direction(8)] = '-'
        move_promoted = move_list[1]
        self.promoted: Optional[Dict[Direction, str]]
        if move_promoted is None:
            self.promoted = None
        else:
            self.promoted = {
                d: move_promoted[x] for x, d in enumerate(Direction.valid())
            }
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

    def __repr__(self):
        # Using implicit string concatenation here, this is intended
        return (f"{self.__class__.__name__}"
                f"({self.name !r}, {self.color !r}, promoted={self.promoted}")

    def __len__(self) -> int: return len(self.current)

    def can_move(self, relative_location: RelativeCoord) -> bool:
        """Check if piece can move to location.

        :param relative_location: relative location of move
        :return: if move is legal
        """

        vec = Direction(relative_location)
        abs_location = abs(relative_location)
        dist = max(abs_location)
        magic_var = self[vec]
        if isinstance(magic_var, int) and not isinstance(magic_var, bool):
            return dist == magic_var and relative_location.is_linear()
        elif isinstance(magic_var, list):
            return list(abs_location) == magic_var
        elif isinstance(magic_var, bool):
            return magic_var and relative_location.is_linear()
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
        :return: demoted version of self
        """

        if not self.is_promoted:
            raise DemotedException
        return Moves(self.name, self.color, False)


class PieceMove:
    """The class representing a move rank for a piece.

    This class is used for the representation of all possible moves
    for the piece.

    :ivar move_function: function for move
    """

    def __init__(self, move_var: str):
        """Initialise instance of PieceMove.

        :param move_var: string detailing the move
        """
        self.move_function: MoveFnLike = _move_functions[move_var]

    def try_move(self, move: RelativeCoord) -> bool:
        return self.move_function(move)


def _hyphen(_move: RelativeCoord) -> bool:
    return False


def _one(move: RelativeCoord) -> bool:
    return max(abs(move)) == 1


def _plus(move: RelativeCoord) -> bool:
    if move.x == move.y:
        return True
    elif any(move) and not all(move):
        return True
    else:
        return False


def _t_move(move: RelativeCoord) -> bool:
    return abs(move.x) == 1 and abs(move.y) == 2


_move_functions: Dict[str, Callable] = {
    '-': _hyphen,
    '1': _one,
    '+': _plus,
    'T': _t_move,
}

_valid_colors = tuple(Color(x) for x in range(2))
