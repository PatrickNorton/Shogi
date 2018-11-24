from Shogiclasses import board, pathjoin


def playgame():
    global theboard
    theboard = board()
    game = True
    with open(pathjoin('shogierrors.txt')) as etxt:
        etxt = etxt.readlines()
        errorlist = [x.strip() for x in etxt]
    while game:
        print(board)
        print(f"{repr(theboard.currplyr)}'s turn")
        game = piececheck()
        check, kingpos, checklist = checkcheck()
        if check and game:
            mate = matecheck(kingpos, checklist)
            game = not mate
            if mate:
                print(board)
                print(f"Checkmate! {repr(board.currplyr)} wins!")
        board.currplyr = board.currplyr.flip()


def piececheck():
    global theboard
    game, quitting, error = True, False, 1
    while not error:
        pieceloc = input('Where is the piece you want to move?')
        if inputpiece(pieceloc, quitting):
            pieceloc = inp2loc(pieceloc)
            if theboard[pieceloc].color == theboard.currplyr:
                quitting = movecheck(pieceloc)


def movecheck(current):
    global board
    test, quitting = False, False
    while not test:
        moveloc = input('Where do you want to move this piece?')
        if inputpiece(moveloc, quitting):
            test = True
            moveloc = inp2loc(moveloc)
            promote, theboard = movecheck2(current, moveloc)
            if promote:
                topromote = input('Would you like to promote this piece? ')
                if topromote.lower().startswith('y'):
                    board[moveloc].promote()
    return quitting


def checkcheck():
    pass


def matecheck(kingpos, checklist):
    pass


def inputpiece(pieceloc, quitting):
    pass