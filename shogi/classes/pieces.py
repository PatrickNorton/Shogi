from typing import Optional, Tuple, Set

from .exceptions import (
    NotPromotableException, PromotedException, DemotedException
)
from .information import info
from .locations import RelativeCoord, Direction
from .pieceattrs import Color, ColorLike, Moves, Rank, RankLike

__all__ = [
    "Piece",
    "NoPiece",
]


class Piece:
    """The class representing a piece.

    :ivar rank: rank of piece
    :ivar moves: legal moves for piece
    :ivar color: color of piece
    :ivar tup: (rank, color)
    :ivar prom: if piece is promoted
    :ivar is_promotable: if piece is promotable
    :ivar auto_promote: where the piece must promote
    """

    def __init__(
            self,
            rank: RankLike,
            color: ColorLike,
            promoted: bool = False
    ):
        """Initialise instance of Piece.

        :param rank: 1-letter rank of piece
        :param color: 1-letter color of piece
        """

        if promoted is None:
            promoted = False
        self.rank: Rank = Rank(rank, promoted=promoted)
        self.moves: Moves = Moves(self.rank, Color(color), promoted=promoted)
        self.color: Color = Color(color)
        self.tup: Tuple[Rank, Color] = (self.rank, self.color)
        self.prom: Optional[bool]
        self.is_promotable: bool
        if self.moves.promoted is None:
            self.prom = None
            self.is_promotable = False
        else:
            self.prom = False
            self.is_promotable = True
        if promoted:
            self.prom = True
        other_attributes: dict = info.piece_info[str(rank).lower()]
        self.auto_promote: int = other_attributes['autopromote']

    def __str__(self):
        return str(self.rank) + str(self.color)

    def __eq__(self, other: 'Piece') -> bool: return self.tup == other.tup

    def __bool__(self): return not isinstance(self, NoPiece)

    def __hash__(self): return hash(self.tup)

    def __repr__(self): return f"{self.color !r} {self.rank !r}"

    def promote(self) -> 'Piece':
        """Promote piece.

        :raises NotPromotableException: piece is not promotable
        :raises PromotedException: piece is already promoted
        :return: promoted piece
        """

        if self.prom is None:
            raise NotPromotableException
        elif self.prom:
            raise PromotedException
        else:
            return Piece(self.rank, self.color, promoted=True)

    def demote(self) -> 'Piece':
        """Demote piece.

        :raises DemotedException: piece is not promoted
        :return: demoted piece
        """
        if not self.prom:
            raise DemotedException
        else:
            return Piece(self.rank, self.color)

    def flip_sides(self) -> 'Piece':
        """Change sides piece is on.

        :return: flipped-color piece
        """
        return Piece(
            str(self.rank),
            self.color.other_color,
            promoted=self.prom
        )

    def can_move(self, relative_location: RelativeCoord) -> bool:
        """Check if piece can move to location.

        :param relative_location: relative location of move
        :return: whether or not piece can move
        """

        return self.moves.can_move(relative_location)

    def valid_spaces(self, direct: Direction) -> Set[RelativeCoord]:
        """Get spaces piece could move in a direction

        :param direct: direction to be checked
        :return: list of valid relative spaces
        """

        magic_var = self.moves[direct]
        if not magic_var:
            return set()
        elif isinstance(magic_var, bool):
            # If the move rank is a boolean, then it either
            # represents a range of motion, or no motion at all.
            # If it represents a range, add that range to valid.
            # False should already have been caught, so we can ignore
            # that case
            return {
                RelativeCoord(x * direct)
                for x in RelativeCoord.positive_xy()
            }
        elif isinstance(magic_var, int):
            # If the move rank is an integer, then the only valid
            # move is n spaces in the direction, so add that to the
            # valid moves
            return {RelativeCoord(direct) * magic_var}
        elif isinstance(magic_var, list):
            # If the move rank is a list, that represents a move that
            # is different in the x and y directions, so the valid
            # move should be that, in the direction of the move
            return {RelativeCoord(
                (magic_var[0] * direct.x, magic_var[1] * direct.y)
            )}

    def same_color(self, other: 'Piece') -> bool:
        """Check if piece has the same color as another piece.

        :param other: the piece to be compared
        :return: if they have the same color
        """

        return self.color == other.color

    def same_rank(self, other: 'Piece') -> bool:
        """Check if piece is the same rank as another piece.

        :param other: the piece to be compared
        :return: if they are the same rank
        """

        return self.rank == other.rank

    def is_color(self, color: ColorLike) -> bool:
        """Check if piece is of a certain color.

        This can take either a Color, an int, or a str object. It
        should be used as a replacement for "instance.color ==
        Color('x'), as that is more verbose than necessary.

        :param color: color to be compared to
        :return: if the piece is of that color
        """

        if isinstance(color, Color):
            return self.color == color
        elif isinstance(color, str):
            return str(self.color) == color
        elif isinstance(color, int):
            return int(self.color) == color
        return False

    def is_rank(self, rank: RankLike) -> bool:
        """Check if piece is of a certain rank.

        This can take either a Rank or a str object. It should
        be used as a replacement for "instance.rank ==
        Rank('x')", as that is more verbose than necessary.

        :param rank: rank to be tested
        :return: if the piece is of that rank
        """

        if isinstance(rank, Rank):
            return self.rank == rank
        elif isinstance(rank, str):
            return str(self.rank) == rank
        return False

    def is_piece(
            self,
            rank: RankLike,
            color: ColorLike
    ) -> bool:
        """Check if the piece is of a certain color and rank

        :param rank: rank to check
        :param color: color to check
        :return: if the piece is of the same rank and color
        """

        return self.is_rank(rank) and self.is_color(color)


class NoPiece(Piece):
    """The "null" instance of a piece."""

    def __init__(self):
        super().__init__('-', '-')

    def __repr__(self): return 'NoPiece()'
