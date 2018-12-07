from Shogiclasses import piece, board, direction, coord, pathjoin, IllegalMove, row
from copy import deepcopy
from itertools import product

# TODO: Split checkcheck into 2 parts:
# TODO: First, check if current piece checks opp. king
# TODO: Second, check if any piece in line btwn. king
# TODO:  and original loc. can attack king
# TODO: Add fn for not moving king into check


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
            theboard.currplyr = theboard.currplyr.flip()
            continue
        theboard.lastmove = theboard.nextmove
        check, kingpos, checklist = checkcheck(*(theboard.lastmove))
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
        theboard.currplyr = theboard.currplyr.flip()


def piececheck():
    global theboard
    game, validpiece = True, False
    while not validpiece:
        pieceloc = input('Where is the piece you want to move? ')
        validpiece = inputpiece(pieceloc)
    pieceloc = coord(pieceloc)
    if theboard[pieceloc].COLOR == theboard.currplyr:
        movecheck(pieceloc)
    else:
        raise IllegalMove(5)
    return game


def movecheck(current):
    global theboard
    validpiece = False
    while not validpiece:
        moveloc = input('Where do you want to move this piece? ')
        validpiece = inputpiece(moveloc)
    moveloc = coord(moveloc)
    promote, theboard = movecheck2(current, moveloc)
    theboard.nextmove = (current, moveloc)
    canpromote = theboard[moveloc].PROMOTABLE
    ispromoted = theboard[moveloc].prom
    if promote and canpromote and not ispromoted:
        topromote = input('Would you like to promote this piece? ')
        if topromote.lower().startswith('y'):
            theboard[moveloc].promote()


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


def checkcheck(oldloc, newloc, earlybreak=False):
    global theboard
    check, checklist = False, []
    oldboard = deepcopy(theboard)
    toget = piece('k', oldboard.currplyr)
    kingpos = oldboard[toget]
    try:
        movecheck2(newloc, kingpos)
    except IllegalMove:
        check, checklist = checkcheck2(oldloc, kingpos, [], earlybreak)
    else:
        if earlybreak:
            checklist.append(newloc)
            return True, checklist
        else:
            checklist.append(newloc)
            check, checklist = checkcheck2(oldloc, kingpos, checklist, earlybreak)
            return True, checklist
    theboard = deepcopy(oldboard)
    return check, kingpos, checklist


def checkcheck2(oldloc, kingpos, checklist, earlybreak=False):
    global theboard
    relcoord = kingpos-oldloc
    mvmt = abs(relcoord)
    if mvmt.x != mvmt.y and min(mvmt):
        return False, checklist
    toking = direction(relcoord)
    doa = row(oldloc, toking)
    currpieces = theboard.playerpcs()
    pieces = [x for x in doa if x in currpieces]
    for x in pieces:
        try:
            movecheck2(x, kingpos)
        except IllegalMove:
            continue
        else:
            checklist.append(x)
            if earlybreak or len(checklist) > 1:
                return True, checklist
            else:
                continue
    return False, checklist


def kingcheck(oldloc, newloc):
    rowlist = set(direction(x) for x in range(8))
    for x in rowlist:
        for dist in range(9):
            dist = coord(dist)
            loctotest = newloc+x*dist
            try:
                movecheck2(loctotest, newloc)
            except IllegalMove as e:
                if str(e) == '2':
                    return True
                else:
                    continue
            return False
    #TODO: Knights


def matecheck(kingpos, checklist):
    global theboard, captlist
    oldboard = deepcopy(theboard)
    kingmovepos = [coord(direction(x)) for x in range(8)]
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
    haspieces = captlist[int(theboard.currplyr)]
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
    except IndexError:
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
