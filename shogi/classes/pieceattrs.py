from collections.abc import Sequence
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
            # If the inputted value is an integer, then the integer is
            # self.int, and self.name comes from the integer
            self.int = turn_num
            self.name = 'wb'[self.int]
        elif isinstance(turn_num, str):
            # String inputs have an extra possible value: '-', for
            # the color of an instance of NoPiece
            if turn_num == '-':
                self.name = turn_num
                self.int = -1
            # Otherwise, do exactly what would have been done with the
            # integer input, but in "reverse"
            else:
                self.name = turn_num
                self.int = 'wb'.index(turn_num)
        elif isinstance(turn_num, Color):
            # If it's a Color input, set this's attributes to the
            # other's
            self.int = turn_num.int
            self.name = turn_num.name
        else:
            # If the input isn't what was expected, error out
            raise TypeError(
                f"turn_num: Expected {ColorLike}, got {type(turn_num)}"
            )
        # Set the full name of the color
        self.full_name: str = ['White', 'Black'][self.int]

    def __str__(self): return self.name

    def __repr__(self): return f"{self.__class__.__name__}({self.int !r})"

    def __int__(self): return self.int

    def __eq__(self, other):
        if isinstance(other, Color):
            return self.int == other.int

    def __hash__(self): return hash((self.int, self.name))

    @classmethod
    def valid(cls) -> Generator['Color', None, None]:
        yield cls(0)
        yield cls(1)

    @property
    def other(self) -> 'Color':
        """Color: Opposite color from first"""
        return Color(1-self.int)


class Rank:
    """The class for the rank of the piece.

    This class is what determines which rank the piece is (e.g. king,
    rook, knight, etc.). It should be used for comparisons between
    two piece's types.

    :ivar rank: the short name of the piece -- see "help names"
    :ivar name: the full name of the piece
    """
    def __init__(self, rank: RankLike, is_promoted: bool = False):
        """Initialise instance of Rank.

        :param rank: rank of piece ('n', 'b', etc.)
        :param is_promoted: if piece is promoted
        """
        if isinstance(rank, Rank):
            # If rank is a rank, continue along your merry way
            if is_promoted:
                self.rank: str = rank.rank.upper()
            else:
                self.rank: str = rank.rank.lower()
        elif isinstance(rank, str):
            # Otherwise, if the piece is promoted, ensure that
            # self.rank is uppercase, and get the appropriate name
            # info
            if is_promoted:
                self.rank: str = rank.upper()
            # Otherwise, just get the info, and ensure self,rank is
            # lowercase
            else:
                self.rank: str = rank.lower()
        else:
            raise TypeError(f"rank: Expected {RankLike}, got {type(rank)}")
        self.name: str = info.name_info[self.rank]

    def __str__(self): return self.rank

    def __repr__(self):
        # Implicit string concatenation
        return (f"{self.__class__.__name__}"
                f"({self.rank !r}, promoted={self.rank.isupper()})")

    def __eq__(self, other):
        if isinstance(other, Rank):
            return self.name == other.name

    def __hash__(self): return hash((self.rank, self.name))

    @property
    def promoted(self) -> 'Rank':
        """Promote the piece."""
        return Rank(self, is_promoted=True)

    @property
    def demoted(self) -> 'Rank':
        """Demote the piece."""
        return Rank(self, is_promoted=False)


class Moves(Sequence):
    """The class containing the set of moves the piece can do.

    This class contains a dictionary relating directions to the moves
    the piece can make. It also has the ability to test whether or not
    a certain move can be made.

    :ivar name: 1-letter name of piece
    :ivar color: color of piece
    :ivar demoted_moves: direction -> move when not is_promoted
    :ivar promoted_moves: direction -> move when is_promoted
    :ivar moves: (demoted, is_promoted)
    :ivar is_promoted: if the piece is promoted
    :ivar current: current set of moves
    """
    def __init__(
            self,
            piece_name: RankLike,
            color: ColorLike,
            promoted: bool = False
    ):
        """Initialise instance of moves.

        :param piece_name: 1-letter name of piece
        :param color: color of piece
        :param promoted: if piece is promoted
        :raises NotPromotableException: if un-promotable is promoted
        """
        # Coerce all the vars to their respective types
        if not isinstance(piece_name, Rank):
            piece_name = Rank(piece_name)
        if not isinstance(color, Color):
            color = Color(color)
        piece_name = str(piece_name).lower()
        move_list = list(info.move_info[piece_name])
        # If the piece is black, rotate the piece moves around by
        # 180º, so that the moves are proper
        if color.name == 'b':
            move_list = [x and x[4:] + x[:4] for x in move_list]
        move_demoted = move_list[0]
        self.name: str = piece_name
        self.color: Color = color
        self.demoted_moves: Dict[Direction, str] = {
            d: move_demoted[x] for x, d in enumerate(Direction.valid())
        }
        self.demoted_moves[Direction(8)] = '-'
        move_promoted = move_list[1]
        self.promoted_moves: Optional[Dict[Direction, str]]
        # If there is no promoted version of the move, then set
        # promoted_moves to None
        if move_promoted is None:
            self.promoted_moves = None
        else:
            self.promoted_moves = {
                d: move_promoted[x] for x, d in enumerate(Direction.valid())
            }
            self.promoted_moves[Direction(8)] = '-'
        self.moves: tuple = (self.demoted_moves, self.promoted_moves)
        self.is_promoted: bool = promoted
        self.current: Dict[Direction, str] = self.moves[self.is_promoted]
        # If the moves of the current promotion is None, then the
        # piece is not promotable, but was promoted anyways, so
        # something has gone wrong
        if self.current is None:
            raise NotPromotableException

    def __getitem__(self, attr: Union[Direction, int]) -> str:
        if isinstance(attr, Direction):
            return self.current[attr]
        elif isinstance(attr, int):
            return self.current[Direction(attr)]
        else:
            raise TypeError(
                f"getitem: Expected Union[Direction, int], got {type(attr)}"
            )

    def __iter__(self) -> Generator: yield from self.current.values()

    def __repr__(self):
        return (f"{self.__class__.__name__}"
                + f"({self.name !r}, {self.color !r}, "
                + f"promoted_moves={self.promoted_moves})")

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
        if isinstance(magic_var, bool):
            return magic_var and relative_location.is_linear
        elif isinstance(magic_var, int):
            return dist == magic_var and relative_location.is_linear
        elif isinstance(magic_var, list):
            return list(abs_location) == magic_var
        return False

    @property
    def promoted(self) -> 'Moves':
        """Promote self.

        :raises PromotedException: already promoted
        :return: promoted version of self
        """
        if self.is_promoted:
            raise PromotedException
        return Moves(self.name, self.color, promoted=True)

    @property
    def demoted(self) -> 'Moves':
        """Demote self.

        :raises DemotedException: already demoted
        :return: demoted version of self
        """
        if not self.is_promoted:
            raise DemotedException
        return Moves(self.name, self.color, promoted=False)
