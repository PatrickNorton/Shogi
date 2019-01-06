from .pieceattrs import Moves, Color, PieceType
from .locations import Coord, Direction
from .exceptions import (
    NotPromotableException, PromotedException, DemotedException)
from .information import info
from typing import Tuple, Optional, List, Union

__all__ = [
    "Piece",
    "NoPiece"
]


class Piece:
    """The class representing a piece.

    :ivar type: type of piece
    :ivar moves: legal moves for piece
    :ivar color: color of piece
    :ivar tup: (type, color)
    :ivar prom: if piece is promoted
    :ivar is_promotable: if piece is promotable
    :ivar auto_promote: where the piece must promote
    """

    def __init__(
            self,
            typ: Union[str, PieceType],
            clr: Union[int, str, Color]
    ):
        """Initialise instance of Piece.

        :param typ: 1-letter type of piece
        :param clr: 1-letter color of piece
        """

        self.type: PieceType = PieceType(typ)
        self.moves: Moves = Moves(self.type, Color(clr))
        self.color: Color = Color(clr)
        self.tup: Tuple[PieceType, Color] = (self.type, self.color)
        self.prom: Optional[bool]
        self.is_promotable: bool
        if self.moves.promoted is None:
            self.prom = None
            self.is_promotable = False
        else:
            self.prom = False
            self.is_promotable = True
        other_attributes: dict = info.piece_info[str(typ)]
        self.auto_promote: int = other_attributes['auto_promote']

    def __str__(self):
        return str(self.type) + str(self.color)

    def __eq__(self, other: 'Piece') -> bool: return self.tup == other.tup

    def __bool__(self): return not isinstance(self, NoPiece)

    def __hash__(self): return hash(self.tup)

    def __repr__(self): return f"{self.color !r} {self.type !r}"

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
            self.type = self.type.prom()
            self.moves = self.moves.prom()
            self.prom = True
            return self

    def demote(self) -> 'Piece':
        """Demote piece.

        :raises DemotedException: piece is not promoted
        :return: demoted piece
        """

        if not self.prom:
            raise DemotedException
        else:
            self.type = self.type.dem()
            self.moves = self.moves.dem()
            self.prom = False
            return self

    def flip_sides(self) -> 'Piece':
        """Change sides piece is on.

        :return: flipped-color piece
        """

        return Piece(str(self.type), self.color.other_color)

    def can_move(self, relative_location: Coord) -> bool:
        """Check if piece can move to location.

        :param relative_location: relative location of move
        :return: whether or not piece can move
        """

        return self.moves.can_move(relative_location)

    def valid_spaces(self, direct: Direction) -> List[Coord]:
        """Get spaces piece could move in a direction

        :param direct: direction to be checked
        :return: list of valid relative spaces
        """

        magic_var = self.moves[direct]
        valid = []
        if magic_var == '-':
            return []
        elif magic_var == '1':
            valid.append(Coord(direct))
        elif magic_var == 'T':
            xy = (direct.x, 2*direct.y)
            valid.append(Coord(xy))
        elif magic_var == '+':
            for x in range(9):
                x = Coord(x)
                relative_location = x*direct
                if self.can_move(relative_location):
                    valid.append(relative_location)
        return valid

    def same_color(self, other: 'Piece') -> bool:
        """Check if piece has the same color as another piece.

        :param other: the piece to be compared
        :return: if they have the same color
        """

        return self.color == other.color

    def same_type(self, other: 'Piece') -> bool:
        """Check if piece is the same type as another piece.

        :param other: the piece to be compared
        :return: if they are the same type
        """

        return self.type == other.type

    def is_color(self, clr: Union[Color, int, str]) -> bool:
        """Check if piece is of a certain color.

        This can take either a color, an int, or a str object. It
        should be used as a replacement for "instance.color ==
        Color('x'), as that is more verbose than necessary

        :param clr:
        :return:
        """

        if isinstance(clr, Color):
            return self.color == clr
        elif isinstance(clr, str):
            return str(self.color) == clr
        elif isinstance(clr, int):
            return int(self.color) == clr
        return False

    def has_type(self, typ: Union[PieceType, str]) -> bool:
        """Check if piece is of a certain type.

        This can take either a PieceType or a str object. It should
        be used as a replacement for "instance.type ==
        PieceType('x')", as that is more verbose than necessary.

        :param typ: type to be tested
        :return: if the piece is of that type
        """

        if isinstance(typ, PieceType):
            return self.type == typ
        elif isinstance(typ, str):
            return str(self.type) == typ
        return False

    def is_piece(self,
                 typ: Union[PieceType, str],
                 clr: Union[Color, int, str]
                 ) -> bool:
        """Check if the piece is of a certain color and type/

        :param typ: type to check
        :param clr: color to check
        :return: if the piece is of the same type and color
        """

        return self.has_type(typ) and self.is_color(clr)


class NoPiece(Piece):
    """The "null" instance of a piece."""

    def __init__(self):
        super().__init__('-', '-')

    def __repr__(self): return 'NoPiece()'
