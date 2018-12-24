from Shogiclasses import piece, board, direction, coord
from Shogiclasses import IllegalMove, row, color
from prompt_toolkit import print_formatted_text as print
from copy import deepcopy
from itertools import product
import json


class PlayerExit(Exception):
    pass


class OtherMove(Exception):
    pass


def piececheck(session, theboard):
    validpiece = False
    while not validpiece:
        pieceloc = session.prompt('Enter piece location\n: ')
        validpiece = inputpiece(session, theboard, pieceloc)
        if not validpiece:
            raise IllegalMove(11)
    pieceloc = coord(pieceloc)
    if theboard[pieceloc].COLOR != theboard.currplyr:
        raise IllegalMove(5)
    return pieceloc


def movecheck(session, theboard, current):
    validpiece = False
    while not validpiece:
        print(f"The piece is a {repr(theboard[current])} at {current}.")
        moveloc = session.prompt('Enter location to move piece to\n: ')
        validpiece = inputpiece(session, theboard, moveloc)
        if not validpiece:
            raise IllegalMove(11)
    moveloc = coord(moveloc)
    return (current, moveloc)


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


def inputpiece(session, theboard, pieceloc):
    try:
        pieceloc = coord(pieceloc)
        return True
    except (ValueError, IndexError):
        isother = otherconditions(session, theboard, pieceloc)
        if isother:
            raise OtherMove
        else:
            return False


def otherconditions(session, theboard, var):
    if var == 'drop':
        droppiece(session, theboard)
        return True
    if var == 'quit':
        toquit(session)
        raise IllegalMove(0)
    if var == 'help':
        helpdesk(session, theboard)
        raise IllegalMove(0)
    if var[:4] == 'help':
        filenm = var[4:]
        filenm = filenm.strip()
        helpdesk(session, theboard, filenm)
        raise IllegalMove(0)


def droppiece(session, theboard):
    if not theboard.CAPTURED[theboard.currplyr]:
        raise IllegalMove(7)
    moved = session.prompt('Enter piece name to put in play\n> ')
    if moved.startswith('k'):
        moved = 'n'
    try:
        thepiece = piece(moved[0], theboard.currplyr)
        if thepiece in theboard.CAPTURED[theboard.currplyr]:
            moveto = session.prompt('Enter location to place piece\n: ')
            if inputpiece(session, theboard, moveto):
                moveto = coord(moveto)
                theboard.putinplay(thepiece, moveto)
        else:
            raise IllegalMove(10)
    except ValueError:
        pass


def helpdesk(session, theboard, filenm=None):
    with open('shogihelp.txt') as helpf:
        filetxt = helpf.read()
    if filenm is not None:
        if filenm == 'moves':
            movelistfn(session, theboard)
            return
        filenm = ltrtoname(filenm)
        try:
            with open(f"helpfiles/{filenm}.txt") as f:
                thefile = f.read()
            prompt = 'Press Esc to return to game'
            print(thefile)
            session.prompt(prompt)
        except FileNotFoundError:
            toout = 'Invalid help command. Type "help" for command list.\n'
            print(toout)
        return
    prompt = 'Press Esc to activate help menu'
    print(filetxt)
    session.prompt(prompt)
    while True:
        filenm = session.prompt("help: ")
        filenm = filenm.strip()
        filelwr = filenm.lower()
        if filelwr == 'exit':
            break
        elif filelwr == 'quit':
            toquit(session)
        elif filelwr == 'moves':
            movelistfn(session, theboard)
        else:
            filenm = ltrtoname(filenm)
            filenm = filenm.lower()
            try:
                with open(f"helpfiles/{filenm}.txt") as f:
                    thefile = f.read()
                prompt = 'Press Esc to activate help menu'
                print(thefile)
                session.prompt(prompt)
            except FileNotFoundError:
                print('Invalid help command\n')
                with open("helpfiles/helpcommands.txt") as f:
                    commands = f.read()
                print(commands)


def ltrtoname(filenm):
    with open('shoginames.json') as f:
        namedict = json.load(f)
    if filenm.lower() in namedict:
        if filenm.islower():
            filenm = namedict[filenm]
        elif filenm.isupper():
            filenm = '+'+namedict[filenm.lower()]
    return filenm


def setpos(session):
    theboard = board()
    todict = {}
    while True:
        loc = session.prompt('Choose location')
        loc = loc.strip()
        if loc == 'done':
            print('Board completed')
            break
        valid = inputpiece(session, theboard, loc)
        if not valid:
            print('Invalid location')
            continue
        loc = coord(loc)
        pcstr = session.prompt('Choose piece and color ')
        try:
            piecenm = piece(*pcstr)
        except (ValueError, IndexError):
            print('Invalid piece\n')
            continue
        todict[loc] = piecenm
    toreturn = board(todict)
    return toreturn


def toquit(session):
    while True:
        print('You are about to quit the game of Shogi\n')
        toquit = session.prompt('Are you sure you want to quit?')
        if toquit:
            raise PlayerExit
        else:
            break


def movelistfn(session, theboard):
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
    filestr = ''
    for loc, piece in currpieces.items():
        filestr += f"{repr(piece)} at {loc}:\n"
        toprint = (str(x) for x in movedict[loc])
        filestr += f"    {', '.join(toprint)}\n"
    filestr = filestr.strip()
    prompt = "Press Esc to return to game"
    print(filestr)
    session.prompt(prompt)


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
