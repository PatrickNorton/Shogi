from Shogiclasses import piece, board, direction, coord, pathjoin, IllegalMove
from copy import deepcopy
from itertools import product

# TODO: Change quitting to an exception, not a var


class PlayerExit(Exception):
    pass


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
    global theboard
    test, quitting = False, False
    while not test:
        moveloc = input('Where do you want to move this piece?')
        if inputpiece(moveloc, quitting):
            test = True
            moveloc = inp2loc(moveloc)
            legal, promote, theboard = movecheck2(current, moveloc)
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
    return not error, topromote and not error, theboard


def obscheck(current, new, move):
    global error
    movedir = direction(move)
    for x in range(1, max(abs(move))):
        testpos = current+coord((x*z for z in movedir))
        if board[current+testpos]:
            error = 2


def checkcheck(earlybreak=False):
    global theboard
    check, checklist = False, []
    oldboard = deepcopy(theboard)
    toget = piece('k', str(oldboard.currplyr))
    kingpos = oldboard[toget]
    for loc in theboard.it():
        loc = coord(loc)
        if theboard[loc].COLOR == theboard.currplyr:
            if movecheck2(loc, kingpos)[0]:
                check = True
                checklist.append(loc)
                if len(checklist) >= 2 or earlybreak:
                    theboard = deepcopy(oldboard)
                    break
        theboard = deepcopy(oldboard)
    return check, kingpos, checklist


def matecheck(kingpos, checklist):
    global theboard, error
    oldboard = deepcopy(theboard)
    kingmovepos = [coord(direction(x)) for x in range(8)]
    for kmpiter in kingmovepos:
        newpos = kmpiter+kingpos
        if tuple(newpos) in theboard.it():
            legal = movecheck2(kingpos, newpos)[0]
            board = deepcopy(oldboard)
            if legal and not checkcheck(True)[0]:
                return False
    if len(checklist) == 1:
        checklist = checklist[0]
        haspieces = captlist[int(board.currplyr)]
        notknight = str(board[checklist].PTYPE) != 'n'
        hasspace = not all(x in (-1, 0, 1) for x in newpos)
        if haspieces and notknight and hasspace:
            return False
        for loc in theboard.occupied():
            enemypc = theboard[loc].COLOR == theboard.currplyr.flip()
            if enemypc:
                legal = movecheck2(loc, checklist)
                if legal:
                    board = deepcopy(oldboard)
                    return False
                theboard = deepcopy(oldboard)
        move = kingpos-checklist
        movedir = direction(move)
        for pos, z in product(theboard.occupied(), range(abs(max(move)))):
            enemypc = theboard[pos].COLOR == theboard.currplyr.flip()
            if enemypc:
                newpos = z*checklist*coord(movedir)
                legal = movecheck2(pos, newpos)
                if legal:
                    board = deepcopy(oldboard)
                    return False
                board = deepcopy(oldboard)
    return True


def inputpiece(pieceloc):
    try:
        pieceloc = coord(pieceloc)
        return True
    except IndexError:
        isother = otherconditions(pieceloc)
        return isother


def otherconditions(var):
    global theboard
    if var == 'captured':
        droppiece()
    if var == 'quit':
        willquit = input('Are you sure you want to quit? (y/n) ')
        if willquit.startswith('y'):
            raise PlayerExit


def droppiece():
    global theboard
    moved = input('Which piece do you want put in play? ')
    try:
        thepiece = piece(moved[0], theboard.currplyr)
        if thepiece in theboard.CAPTURED[theboard.currplyr]:
            moveto = input('Where do you want it moved? ')
            if inputpiece(moveto):
                try:
                    theboard.putinplay(moveto)
                except IllegalMove:
                    pass
    except IndexError:
        pass


def inp2loc(pieceloc):
    pass
