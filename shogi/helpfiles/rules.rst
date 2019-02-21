.. _rules:

Rules of shogi
==============

Shogi is a chess-style Japanese board game.

.. _rules_objective:

Objective
---------

To checkmate the king. See "`Checkmate`_", below.

.. _rules_movement:

Movement
--------

For detailed rules on movement, type the piece's first letter into the prompt.

.. _rules_promotion:

Promotion
---------

A piece may be promoted when it reaches the furthest three rows from it. These
are rows a-c for white, and rows g-i for black.
When a piece is eligible to be promoted, a prompt appears after the move. If
you wish to promote the piece, type 'y' and press Return. Otherwise, type 'n'.
A piece may only be promoted on a turn in which it is moved. If a piece
reaches a position in the board from which it cannot further move unless it is
promoted, it must promote, and is automatically promoted.

.. _rules_drop:

Drops
-----

Captured pieces are retained by the capturing player, and may be dropped onto
any empty space on the board. Pieces may not be promoted on the turn they are
dropped.

Restrictions on drops:
    1. A pawn may not be dropped onto a file containing another pawn of the
       same player.
    2. A pawn may not be dropped to give immediate checkmate.
    3. A piece may not be dropped somewhere where it must be promoted.

.. _rules_check:

Check
-----

When a player's move threatens to capture the king on the next turn, the king
is in check. Any player whose king is in check must, on their next move,
remove the check.
The program announces check when it happens.

.. Not yet, it'll happen...

.. _rules_checkmate:

Checkmate
---------

When a player is in check and has no possible move which could remove them from
check, they are in checkmate. If a player is checkmated, they lose.
The program announces checkmate when it happens, and ends the game.
