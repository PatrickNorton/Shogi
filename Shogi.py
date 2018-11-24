from Shogiclasses import board, direction, coord, pathjoin
from copy import deepcopy


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
    return not quitting and game


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


def movecheck2(current, new):
    global theboard, captlist, error
    newboard = deepcopy(theboard)
    piece = newboard[current]
    move = new-current
    movedir = direction(move)
    magicvar = piece.MOVES[movedir]
    error = 0
    if movedir == direction(8):
        error = 3
    elif board[new].COLOR == board.currplyr:
        error = 4
    elif not piece.canmove(move):
        error = 1
    elif magicvar == 'T':
        error = 0
    else:
        obscheck(current, new, move)
    if not error:
        newboard.move(current, new)
    topromote = board[new].PROMOTABLE and board.canpromote(new)
    return topromote and not error, theboard


def obscheck(current, new, move):
    global error
    movedir = direction(move)
    for x in range(1, max(abs(move))):
        testpos = current+coord((x*z for z in movedir))
        if board[current+testpos]:
            error = 2


def checkcheck():
    pass


def matecheck(kingpos, checklist):
    pass


def inputpiece(pieceloc, quitting):
    pass
