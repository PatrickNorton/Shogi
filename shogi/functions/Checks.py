from shogi.classes import piece, board, direction, coord
from shogi.classes import IllegalMove, row, color
from prompt_toolkit import print_formatted_text as print
from copy import deepcopy
from itertools import product
import json


class PlayerExit(Exception):
    pass


class OtherMove(Exception):
    pass


class OtherInput(Exception):
    pass


def piececheck(theboard, pieceloc):
    validpiece = inputpiece(theboard, pieceloc)
    if not validpiece:
        raise IllegalMove(11)
    pieceloc = coord(pieceloc)
    if theboard[pieceloc].COLOR != theboard.currplyr:
        raise IllegalMove(5)
    return pieceloc


def movecheck(theboard, current, moveloc):
    validpiece = inputpiece(theboard, moveloc)
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


def inputpiece(theboard, pieceloc):
    try:
        pieceloc = coord(pieceloc)
        return True
    except (ValueError, IndexError):
        raise OtherInput(pieceloc)
