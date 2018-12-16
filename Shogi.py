from Shogiclasses import piece, board, direction, coord
from Shogiclasses import IllegalMove, row, color
from copy import deepcopy
from itertools import product
import json
import curses
import time


class PlayerExit(Exception):
    pass


class OtherMove(Exception):
    pass


def playgame(stdscr):
    theboard = board()
    game = True
    debug = False
    if debug:
        theboard = setpos(stdscr)
    with open('shogierrors.json') as etxt:
        errorlist = json.load(etxt)
    while game:
        stdscr.clear()
        stdscr.addstr(str(theboard))
        stdscr.addstr(f"{repr(theboard.currplyr)}'s turn\n")
        try:
            piececheck(stdscr, theboard)
            tocc = (theboard, theboard.nextmove, theboard.currplyr, True)
            ccvars = checkcheck(*tocc)
            check = ccvars[0]
            if check:
                raise IllegalMove(6)
        except IllegalMove as e:
            var = int(str(e))
            if var:
                stdscr.addstr(f"Error: {errorlist[var]}\n")
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
                stdscr.addstr(theboard)
                stdscr.addstr(f"Checkmate. {repr(theboard.currplyr)} wins\n")
                game = False
                break
            else:
                stdscr.addstr('Check\n')
        theboard.currplyr = theboard.currplyr.other()


def piececheck(stdscr, theboard):
    validpiece = False
    while not validpiece:
        pieceloc = getinput(stdscr, 'Enter piece location\n: ')
        validpiece = inputpiece(stdscr, theboard, pieceloc)
        if not validpiece:
            stdscr.addstr('Invalid piece\n')
    pieceloc = coord(pieceloc)
    if theboard[pieceloc].COLOR == theboard.currplyr:
        movecheck(stdscr, theboard, pieceloc)
    else:
        raise IllegalMove(5)


def movecheck(stdscr, theboard, current):
    validpiece = False
    while not validpiece:
        stdscr.addstr(f"The piece is a {repr(theboard[current])} at {current}.\n")
        moveloc = getinput(stdscr, 'Enter location to move piece to\n: ')
        validpiece = inputpiece(stdscr, theboard, moveloc)
        if not validpiece:
            stdscr.addstr('Invalid piece\n')
    moveloc = coord(moveloc)
    promote = movecheck2(theboard, (current, moveloc))
    theboard.nextmove = (current, moveloc)
    canpromote = theboard[moveloc].PROMOTABLE
    ispromoted = theboard[moveloc].prom
    if promote and canpromote and not ispromoted:
        if theboard.autopromote(moveloc):
            theboard[moveloc] = theboard[moveloc].promote()
        else:
            while True:
                stdscr.addstr('Promote this piece? (y/n)\n] ')
                topromote = stdscr.getch()
                topromote = topromote.decode("utf-8")
                if topromote.lower().startswith('y'):
                    theboard[moveloc] = theboard[moveloc].promote()
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
        kingcheck(theboard, (current, new))
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
    kingpos = theboard.getpiece(toget)
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
    pieces = (x for x in doa if x in currpieces)
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
    rowlist = (direction(x) for x in range(8))
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
    kingmovepos = (coord(direction(x)) for x in range(8))
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


def inputpiece(stdscr, theboard, pieceloc):
    try:
        pieceloc = coord(pieceloc)
        return True
    except (ValueError, IndexError):
        isother = otherconditions(stdscr, theboard, pieceloc)
        if isother:
            raise OtherMove
        else:
            return False


def otherconditions(stdscr, theboard, var):
    if var == 'drop':
        droppiece(stdscr, theboard)
        return True
    if var == 'quit':
        toquit(stdscr)
        raise IllegalMove(0)
    if var == 'help':
        helpdesk(stdscr, theboard)
        raise IllegalMove(0)
    if var[:4] == 'help':
        filenm = var[4:]
        filenm = filenm.strip()
        helpdesk(stdscr, theboard, filenm)
        stdscr.addstr('Press any key to return to game.\n')
        stdscr.getch()
        raise IllegalMove(0)


def droppiece(stdscr, theboard):
    if not theboard.CAPTURED[theboard.currplyr]:
        raise IllegalMove(7)
    moved = getinput(stdscr, 'Enter piece name to put in play\n> ')
    if moved.startswith('k'):
        moved = 'n'
    try:
        thepiece = piece(moved[0], theboard.currplyr)
        if thepiece in theboard.CAPTURED[theboard.currplyr]:
            moveto = getinput(stdscr, 'Enter location to place piece\n: ')
            if inputpiece(stdscr, theboard, moveto):
                moveto = coord(moveto)
                theboard.putinplay(thepiece, moveto)
        else:
            raise IllegalMove(10)
    except ValueError:
        pass


def helpdesk(stdscr, theboard, filenm=None):
    with open('shogihelp.txt') as helpf:
        filetxt = helpf.read()
    stdscr.clear()
    stdscr.scrollok(True)
    if filenm is not None:
        if filenm == 'moves':
            movelistfn(stdscr, theboard)
            return
        filenm = ltrtoname(filenm)
        try:
            with open(f"helpfiles/{filenm}.txt") as f:
                thefile = f.read()
            stdscr.addstr(thefile+'\n')
        except FileNotFoundError:
            stdscr.addstr('Invalid help command. Type "help" for command list.\n')
        return
    stdscr.addstr(filetxt+'\n')
    while True:
        filenm = getinput(stdscr, 'help: ')
        filenm = filenm.strip()
        filelwr = filenm.lower()
        if filelwr == 'exit':
            stdscr.addstr('Returning to game\n')
            break
        elif filelwr == 'quit':
            toquit(stdscr)
        elif filelwr == 'moves':
            movelistfn(stdscr, theboard)
        else:
            filenm = ltrtoname(filenm)
            filenm = filenm.lower()
            try:
                with open(f"helpfiles/{filenm}.txt") as f:
                    thefile = f.read()
                stdscr.addstr(thefile+'\n')
            except FileNotFoundError:
                stdscr.addstr('Invalid help command\n')


def ltrtoname(filenm):
    with open('shoginames.json') as f:
        namedict = json.load(f)
    if filenm.lower() in namedict:
        if filenm.islower():
            filenm = namedict[filenm]
        elif filenm.isupper():
            filenm = '+'+namedict[filenm.lower()]
    return filenm


def setpos(stdscr):
    theboard = board()
    todict = {}
    while True:
        loc = getinput(stdscr, 'Choose location\n')
        loc = loc.strip()
        if loc == 'done':
            stdscr.addstr('Board completed\n')
            break
        valid = inputpiece(stdscr, theboard, loc)
        if not valid:
            stdscr.addstr('Invalid location\n')
            continue
        loc = coord(loc)
        pcstr = getinput(stdscr, 'Choose piece and color ')
        try:
            piecenm = piece(*pcstr)
        except (ValueError, IndexError):
            stdscr.addstr('Invalid piece\n')
            continue
        todict[loc] = piecenm
    toreturn = board(todict)
    return toreturn


def toquit(stdscr):
    while True:
        stdscr.addstr('You are about to quit the game of Shogi\n')
        stdscr.addstr('Are you sure you want to quit? (y/n)\n] ')
        willquit = stdscr.getkey()
        if willquit.startswith('y'):
            raise PlayerExit
        elif willquit.startswith('n'):
            return


def movelistfn(stdscr, theboard):
    movedict = {}
    currpieces = theboard.currpcs()
    for loc, apiece in currpieces.items():
        movelst = []
        dirlist = (direction(x) for x in range(8))
        for x in dirlist:
            tolst = apiece.validspaces(x)
            tolst = testspcs(theboard, loc, tolst)
            movelst += tolst
        movedict[loc] = movelst
    for loc, piece in currpieces.items():
        stdscr.addstr(f"{repr(piece)} at {loc}:\n")
        toprint = (str(x) for x in movedict[loc])
        stdscr.addstr(f"    {', '.join(toprint)}\n")


def testspcs(theboard, pieceloc, spacelist):
    toreturn = []
    for relloc in spacelist:
        try:
            absloc = pieceloc+relloc
            movecheck2(theboard, (pieceloc, absloc))
        except (TypeError, ValueError, IllegalMove):
            continue
        else:
            toreturn.append(absloc)
    return toreturn


def main(stdscr):
    import os
    import sys
    os.chdir(sys.path[0])
    curses.nonl()
    while True:
        try:
            stdscr.clear()
            playgame(stdscr)
            stdscr.addstr('Would you like to play again? ')
            again = stdscr.getkey()
            if not again.startswith('y'):
                break
        except PlayerExit:
            break


def getinput(stdscr, msg, yn=False):
    stdscr.addstr(msg)
    currloc = stdscr.getyx()
    curses.echo()
    toreturn = b''
    while toreturn == b'':
        stdscr.move(*currloc)
        toreturn = stdscr.getstr()
    curses.noecho()
    toreturn = toreturn.decode("utf-8")
    return toreturn


if __name__ == "__main__":
    curses.wrapper(main)
