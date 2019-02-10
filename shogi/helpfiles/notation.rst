Shogi Notation
==============

Basic Notation
--------------

The basic shogi notation is of the form [Piece]-[Location].
This is what most moves consist of, but some are more complex.

Identical Moves
---------------

If two pieces could move to the same location, a differentiating coordinate is
added after the piece.
Only one half of a coordinate is ever added, to save space.

Middle Dash
-----------

If the previous move was a capture, the dash is replaced by an x.
On the drop of a piece, the dash is replaced with a *.

Add-ons
-------

\^
    Piece was promoted
\=
    Piece could promote, but didn't
\+
    Check
\#
    Checkmate

Examples
--------

g-e5
    Gold general moved to e5
B6-e7
    Promoted bishop in column 6 moved to e7
kxc3
    King moved to c3, capturing a piece
l*d7
    Lance dropped at d7
n-h5^
    Knight moved to h5, and promoted
s-a4=
    Silver general moved to a4, did not promote
p-b5+
    Pawn moved to b5, check
rxf7#
    Rook captured at f7, checkmate
