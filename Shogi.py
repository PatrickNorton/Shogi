from Shogiclasses import piece, board, direction, coord, pathjoin, IllegalMove
from copy import deepcopy
from itertools import product

# TODO: Fix what to do when input is not a piece


class PlayerExit(Exception):
    pass


class OtherMove(Exception):
    pass


def playgame():
    global theboard
    theboard = board()
    game = True
    with open(pathjoin('shogierrors.txt')) as etxt:
        etxt = etxt.readlines()
        errorlist = [x.strip() for x in etxt]
    while game:
        print(theboard)
        print(f"{repr(theboard.currplyr)}'s turn")
        try:
            game = piececheck()
        except IllegalMove as e:
            var = int(str(e))
            print(errorlist[var])
            continue
        except OtherMove:
            theboard.currplyr = theboard.currplyr.other()
            continue
        check, kingpos, checklist = checkcheck()
        if check and game:
            mate = matecheck(kingpos, checklist)
            game = not mate
            if mate:
                print(theboard)
                print(f"Checkmate! {repr(theboard.currplyr)} wins!")
                game = False
                break
            else:
                print('Check!')
        theboard.currplyr = theboard.currplyr.other()


def piececheck():
    global theboard
    game, quitting = True, False
    while True:
        pieceloc = input('Where is the piece you want to move? ')
        if inputpiece(pieceloc):
            break
        print('That is not a valid piece!')
    pieceloc = coord(pieceloc)
    if theboard[pieceloc].COLOR == theboard.currplyr:
        quitting = movecheck(pieceloc)
    else:
        raise IllegalMove(5)
    return not quitting and game


def movecheck(current):
    global theboard
    quitting = False
    while True:
        moveloc = input('Where do you want to move this piece? ')
        if inputpiece(moveloc):
            break
        print('That is not a valid piece!')
    moveloc = coord(moveloc)
    promote, theboard = movecheck2(current, moveloc)
    canpromote = theboard[moveloc].PROMOTABLE
    ispromoted = theboard[moveloc].prom
    if promote and canpromote and not ispromoted:
        topromote = input('Would you like to promote this piece? ')
        if topromote.lower().startswith('y'):
            theboard[moveloc].promote()
    return quitting


def movecheck2(current, new):
    global theboard
    newboard = deepcopy(theboard)
    piece = newboard[current]
    move = new-current
    movedir = direction(move)
    magicvar = piece.MOVES[movedir]
    if movedir == direction(8):
        raise IllegalMove(3)
    elif theboard[new].COLOR == theboard.currplyr:
        raise IllegalMove(4)
    elif not piece.canmove(move):
        raise IllegalMove(1)
    elif magicvar == 'T':
        pass
    else:
        obscheck(current, new, move)
    theboard.move(current, new)
    topromote = theboard[new].PROMOTABLE and theboard.canpromote(new)
    return topromote, theboard


def obscheck(current, new, move):
    global theboard
    movedir = direction(move)
    for x in range(1, max(abs(move))):
        testpos = current+coord((x*z for z in movedir))
        if theboard[current+testpos]:
            raise IllegalMove(2)


def checkcheck(earlybreak=False):
    global theboard
    check, checklist = False, []
    oldboard = deepcopy(theboard)
    toget = piece('k', oldboard.currplyr)
    kingpos = oldboard[toget]
    for loc in theboard.it():
        loc = coord(loc)
        if theboard[loc].COLOR == theboard.currplyr:
            try:
                movecheck2(loc, kingpos)[0]
            except IllegalMove:
                continue
            check = True
            checklist.append(loc)
            if len(checklist) >= 2 or earlybreak:
                theboard = deepcopy(oldboard)
                break
        theboard = deepcopy(oldboard)
    return check, kingpos, checklist


def matecheck(kingpos, checklist):
    global theboard
    oldboard = deepcopy(theboard)
    kingmovepos = [direction(x) for x in range(8)]
    for kmpiter in kingmovepos:
        newpos = kmpiter+kingpos
        if tuple(newpos) in theboard.it():
            try:
                movecheck2(kingpos, newpos)
            except IllegalMove:
                theboard = deepcopy(oldboard)
                continue
            theboard = deepcopy(oldboard)
            if not checkcheck(True)[0]:
                return False
    if len(checklist) > 1:
        return True
    checklist = checklist[0]
    haspieces = theboard.CAPTURED[theboard.currplyr]
    notknight = str(theboard[checklist].PTYPE) != 'n'
    hasspace = not all(x in (-1, 0, 1) for x in newpos)
    if haspieces and notknight and hasspace:
        return False
    for loc in theboard.enemypcs():
        try:
            movecheck2(loc, checklist)
        except IllegalMove:
            theboard = deepcopy(oldboard)
            continue
        theboard = deepcopy(oldboard)
        return False
    move = kingpos-checklist
    movedir = direction(move)
    for pos, z in product(theboard.enemypcs(), range(abs(max(move)))):
        newpos = z*checklist*coord(movedir)
        try:
            movecheck2(pos, newpos)
        except IllegalMove:
            theboard = deepcopy(oldboard)
            continue
        theboard = deepcopy(oldboard)
        return False
    return True


def inputpiece(pieceloc):
    try:
        pieceloc = coord(pieceloc)
        return True
    except (ValueError, IndexError):
        isother = otherconditions(pieceloc)
        if isother:
            raise OtherMove
        else:
            return False


def otherconditions(var):
    global theboard
    if var == 'drop':
        droppiece()
        return True
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
                    print('Illegal move!')
    except ValueError:
        pass


while True:
    try:
        playgame()
        again = input('Would you like to play again? ')
        if not again.startswith('y'):
            break
    except PlayerExit:
        break
