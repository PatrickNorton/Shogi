from Shogiclasses import piece, board, direction, coord
from Shogiclasses import IllegalMove, row, color
from copy import deepcopy
from itertools import product


class PlayerExit(Exception):
    pass


class OtherMove(Exception):
    pass


def playgame():
    theboard = board()
    game = True
    debug = False
    if debug:
        theboard = setpos()
    with open('shogierrors.txt') as etxt:
        etxt = etxt.readlines()
        errorlist = [x.strip() for x in etxt]
    while game:
        print(theboard)
        print(f"{repr(theboard.currplyr)}'s turn")
        try:
            piececheck(theboard)
            tocc = (theboard, theboard.nextmove, theboard.currplyr, True)
            ccvars = checkcheck(*tocc)
            check = ccvars[0]
            if check:
                raise IllegalMove(6)
        except IllegalMove as e:
            var = int(str(e))
            if var:
                print(f"Error: {errorlist[var]}")
            continue
        except OtherMove:
            theboard.currplyr = theboard.currplyr.other()
            continue
        theboard.move(*theboard.nextmove)
        theboard.lastmove = theboard.nextmove
        clr = theboard.currplyr.other()
        ccvars = checkcheck(theboard, theboard.lastmove, clr)
        check, kingpos, checklist = ccvars
        if check and game:
            mate = matecheck(theboard, kingpos, checklist)
            game = not mate
            if mate:
                print(theboard)
                print(f"Checkmate. {repr(theboard.currplyr)} wins")
                game = False
                break
            else:
                print('Check')
        theboard.currplyr = theboard.currplyr.other()


def piececheck(theboard):
    validpiece = False
    while not validpiece:
        print('Enter piece location')
        pieceloc = input(": ")
        validpiece = inputpiece(theboard, pieceloc)
        if not validpiece:
            print('Invalid piece')
    pieceloc = coord(pieceloc)
    if theboard[pieceloc].COLOR == theboard.currplyr:
        movecheck(theboard, pieceloc)
    else:
        raise IllegalMove(5)


def movecheck(theboard, current):
    validpiece = False
    while not validpiece:
        print(f"The piece is a {repr(theboard[current])} at {current}.")
        print('Enter location to move piece to')
        moveloc = input(': ')
        validpiece = inputpiece(theboard, moveloc)
        if not validpiece:
            print('Invalid piece')
    moveloc = coord(moveloc)
    promote = movecheck2(theboard, (current, moveloc))
    theboard.nextmove = (current, moveloc)
    canpromote = theboard[moveloc].PROMOTABLE
    ispromoted = theboard[moveloc].prom
    if promote and canpromote and not ispromoted:
        while True:
            print('Promote this piece? (y/n)')
            topromote = input('] ')
            if topromote.lower().startswith('y'):
                theboard[moveloc].promote()
                break
            if topromote.lower().startswith('n'):
                break


def movecheck2(theboard, coords):
    current, new = coords
    piece = theboard[current]
    move = new-current
    movedir = direction(move)
    magicvar = piece.MOVES[movedir]
    if movedir == direction(8):
        raise IllegalMove(3)
    elif not piece.canmove(move):
        raise IllegalMove(1)
    elif theboard[new].COLOR == theboard[current].COLOR:
        raise IllegalMove(4)
    elif magicvar == 'T':
        pass
    elif str(piece.PTYPE) == 'k':
        kingcheck(current, new)
    else:
        obscheck(theboard, current, move)
    topromote = theboard[new].PROMOTABLE and theboard.canpromote(new)
    return topromote


def obscheck(theboard, current, move):
    movedir = direction(move)
    for x in range(1, max(abs(move))):
        relcoord = [x*k for k in movedir]
        testpos = current+coord(relcoord)
        if theboard[testpos]:
            raise IllegalMove(2)


def checkcheck(theboard, coords, color, earlybreak=False):
    oldloc, newloc = coords
    check, checklist = False, []
    toget = piece('k', color)
    kingpos = theboard[toget]
    try:
        movecheck2(theboard, (newloc, kingpos))
    except IllegalMove:
        tocc2 = ((oldloc, kingpos), [], earlybreak)
        check, checklist = checkcheck2(theboard, *tocc2)
    else:
        if earlybreak:
            checklist.append(newloc)
            return True, kingpos, checklist
        else:
            checklist.append(newloc)
            tocc2 = ((oldloc, kingpos), checklist, earlybreak)
            check, checklist = checkcheck2(theboard, *tocc2)
            return True, kingpos, checklist
    return check, kingpos, checklist


def checkcheck2(theboard, coords, checklist, earlybreak=False):
    oldloc, kingpos = coords
    relcoord = kingpos-oldloc
    mvmt = abs(relcoord)
    if mvmt.x != mvmt.y and min(mvmt):
        return False, checklist
    toking = direction(relcoord)
    doa = row(oldloc, toking)
    currpieces = theboard.playerpcs(theboard[kingpos].COLOR.other())
    pieces = [x for x in doa if x in currpieces]
    for x in pieces:
        try:
            movecheck2(theboard, (x, kingpos))
        except IllegalMove:
            continue
        else:
            checklist.append(x)
            if earlybreak or len(checklist) > 1:
                return True, checklist
            else:
                continue
    return False, checklist


def kingcheck(theboard, coords):
    oldloc, newloc = coords
    rowlist = set(direction(x) for x in range(8))
    for x, dist in product(rowlist, range(9)):
        dist = coord(dist)
        try:
            loctotest = newloc+x*dist
            if theboard[loctotest].COLOR == theboard[oldloc].COLOR:
                raise IllegalMove(4)
            movecheck2(theboard, (loctotest, newloc))
        except (ValueError, IndexError):
            continue
        except IllegalMove as e:
            if str(e) == '2':
                break
            else:
                continue
        else:
            raise IllegalMove(6)
    for delx, dely in product((-1, 1), (-1, 1)):
        relcoord = coord((delx, 2*dely))
        try:
            abscoord = newloc+relcoord
            movecheck2(theboard, (abscoord, newloc))
        except (ValueError, IndexError):
            continue
        except IllegalMove:
            continue
        else:
            raise IllegalMove(6)


def matecheck(theboard, kingpos, checklist):
    kingmovepos = [coord(direction(x)) for x in range(8)]
    for kmpiter in kingmovepos:
        newpos = kmpiter+kingpos
        if tuple(newpos) in theboard.it():
            try:
                movecheck2(theboard, (kingpos, newpos))
            except IllegalMove:
                continue
            else:
                return False
    if len(checklist) > 1:
        return True
    checklist = checklist[0]
    haspieces = theboard.CAPTURED[int(theboard.currplyr)]
    notknight = str(theboard[checklist].PTYPE) != 'n'
    hasspace = not all(x in (-1, 0, 1) for x in newpos)
    if haspieces and notknight and hasspace:
        return False
    for loc in theboard.enemypcs():
        try:
            movecheck2(theboard, (loc, checklist))
        except IllegalMove:
            continue
        return False
    move = kingpos-checklist
    movedir = direction(move)
    for pos, z in product(theboard.enemypcs(), range(abs(max(move)))):
        newpos = z*checklist*coord(movedir)
        try:
            movecheck2(theboard, (pos, newpos))
        except IllegalMove:
            continue
        return False
    return True


def inputpiece(theboard, pieceloc):
    try:
        pieceloc = coord(pieceloc)
        return True
    except (ValueError, IndexError):
        isother = otherconditions(theboard, pieceloc)
        if isother:
            raise OtherMove
        else:
            return False


def otherconditions(theboard, var):
    if var == 'drop':
        droppiece(theboard)
        return True
    if var == 'quit':
        toquit()
        raise IllegalMove(0)
    if var == 'help':
        helpdesk()
        raise IllegalMove(0)
    if var[:4] == 'help':
        filenm = var[4:]
        filenm = filenm.strip()
        helpdesk(filenm)
        raise IllegalMove(0)


def droppiece(theboard):
    if not theboard.CAPTURED[theboard.currplyr]:
        raise IllegalMove(7)
    print('Enter piece name to put in play')
    moved = input('> ')
    if moved.startswith('k'):
        moved = 'n'
    try:
        thepiece = piece(moved[0], theboard.currplyr)
        if thepiece in theboard.CAPTURED[theboard.currplyr]:
            print('Enter location to place piece')
            moveto = input(': ')
            if inputpiece(theboard, moveto):
                moveto = coord(moveto)
                theboard.putinplay(thepiece, moveto)
        else:
            raise IllegalMove(10)
    except ValueError:
        pass


def helpdesk(filenm=None):
    with open('shogihelp.txt') as helpf:
        filetxt = helpf.read()
    if filenm is not None:
        filenm = ltrtoname(filenm)
        try:
            with open(f"helpfiles/{filenm}.txt") as f:
                thefile = f.read()
            print(thefile)
            return
        except FileNotFoundError:
            print('Invalid help command')
    print(filetxt)
    while True:
        filenm = input('help: ')
        filenm = filenm.strip()
        filelwr = filenm.lower()
        if filelwr == 'exit':
            print('Returning to game')
            break
        elif filelwr == 'quit':
            toquit()
        else:
            filenm = ltrtoname(filenm)
            filenm = filenm.lower()
            try:
                with open(f"helpfiles/{filenm}.txt") as f:
                    thefile = f.read()
                print(thefile)
            except FileNotFoundError:
                print('Invalid help command')


def ltrtoname(filenm):
    with open('shoginames.txt') as f:
        namelist = f.readlines()
    for x, y in enumerate(namelist):
        namelist[x] = y.strip().split(': ')
    namedict = {x[0]: x[1] for x in namelist}
    if filenm.lower() in namedict:
        if filenm.islower():
            filenm = namedict[filenm]
        elif filenm.isupper():
            filenm = '+'+namedict[filenm.lower()]
    return filenm


def setpos():
    theboard = board()
    todict = {}
    while True:
        loc = input('Choose location ')
        loc = loc.strip()
        if loc == 'done':
            print('Board completed')
            break
        valid = inputpiece(theboard, loc)
        if not valid:
            print('Invalid location')
            continue
        loc = coord(loc)
        pcstr = input('Choose piece and color ')
        try:
            piecenm = piece(*pcstr)
        except (ValueError, IndexError):
            print('Invalid piece')
            continue
        todict[loc] = piecenm
    toreturn = board(todict)
    return toreturn


def toquit():
    while True:
        print('You are about to quit the game of Shogi')
        print('Are you sure you want to quit? (y/n)')
        willquit = input('] ')
        if willquit.startswith('y'):
            raise PlayerExit
        elif willquit.startswith('n'):
            return


if __name__ == "__main__":
    import os
    import sys
    os.chdir(sys.path[0])
    while True:
        try:
            playgame()
            again = input('Would you like to play again? ')
            if not again.startswith('y'):
                break
        except PlayerExit:
            break
