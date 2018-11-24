from Shogiclasses import board, pathjoin


def playgame():
    theboard = board()
    game = True
    with open(pathjoin('shogierrors.txt')) as etxt:
        etxt = etxt.readlines()
        errorlist = [x.strip() for x in etxt]
    while game:
        print(board)
        print(f"{repr(theboard.currplyr)}'s turn")
        game = piececheck(theboard)
        check, kingpos, checklist = checkcheck(theboard)
        if check and game:
            mate = matecheck(theboard, kingpos, checklist)
            game = not mate
            if mate:
                print(board)
                print(f"Checkmate! {repr(board.currplyr)} wins!")
        board.currplyr = board.currplyr.flip()


def piececheck(theboard):
    pass


def checkcheck(theboard):
    pass


def matecheck(theboard, kingpos, checklist):
    pass