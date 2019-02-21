.. _prompt:

Prompt help
===========

**Note:** This is for text-input mode only

The game of shogi has three types of expected input.
These types are delineated by the character at the start of the prompt.

Location input (**:**)

    This input expects a location on the board.
    Locations are in the form letter+number, for example a7.
    The letter specifies the row, and the number the column on the board.

Piece input (**>**)

    This input expects the name of a piece.
    There are three things you can enter:

        - The first letter of the piece's representation (p, n)
        - The piece's representation on the board (pb, nw)
        - The full name of the piece (pawn, knight)

Binary input (**]**)

    This input expects one of two answers to a question.

    - If the answer is yes, type y
    - If the answer is no, type n
