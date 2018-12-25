from curtsies import FullscreenWindow, Input, fsarray
from curtsies.fmtfuncs import bold
from curtsies.events import PasteEvent
from shogi import Checks
from shogi import Classes
from shogi import Text
import json


def main(input_gen, window):
    theboard = Classes.board()
    game = True
    debug = False
    errstr = ''
    if debug:
        theboard = Text.setpos(input_gen, window)
    with open('datafiles/errors.json') as etxt:
        errorlist = json.load(etxt)
    while game:
        todisp = []
        if errstr:
            todisp.append(bold('Error: '+errstr))
            errstr = ''
        todisp += str(theboard).split('\n')
        todisp.append(f"{repr(theboard.currplyr)}'s turn")
        maindisp = todisp[:]
        todisp.append('Enter piece location')
        todisp.append(': ')
        try:
            pieceloc = Text.getinput(input_gen, window, todisp)
            pieceloc = Checks.piececheck(theboard, pieceloc)
            todisp = maindisp[:]
            astr = f"The piece is a {repr(theboard[pieceloc])} at {pieceloc}."
            todisp.append(astr)
            todisp.append('Enter location to move piece to')
            todisp.append(': ')
            moveloc = Text.getinput(input_gen, window, todisp)
            coords = Checks.movecheck(theboard, pieceloc, moveloc)
            Checks.movecheck2(theboard, coords)
            theboard.nextmove = coords
            tocc = (theboard, theboard.nextmove, theboard.currplyr, True)
            ccvars = Checks.checkcheck(*tocc)
            check = ccvars[0]
            if check:
                raise Classes.IllegalMove(6)
        except Classes.IllegalMove as e:
            var = int(str(e))
            if var:
                errstr = f"Error: {errorlist[var]}"
            continue
        except Checks.OtherInput as e:
            pieceloc = e.args[0]
            try:
                Text.otherconditions(
                    input_gen, window, todisp, theboard, pieceloc
                    )
            except Classes.IllegalMove:
                var = int(str(e))
                if var:
                    errstr = f"Error: {errorlist[var]}"
                    continue
            except Checks.OtherMove:
                theboard.currplyr = theboard.currplyr.other()
                continue
        theboard.move(*theboard.nextmove)
        moveloc = theboard.nextmove[1]
        promote = theboard.canpromote(moveloc)
        canpromote = theboard[moveloc].PROMOTABLE
        ispromoted = theboard[moveloc].prom
        if promote and canpromote and not ispromoted:
            if theboard.autopromote(moveloc):
                theboard.promote(moveloc)
            else:
                todisp.append('Promote this piece? ')
                topromote = Text.yninput(input_gen, window, todisp)
                if topromote:
                    theboard.promote(moveloc)
        theboard.lastmove = theboard.nextmove
        clr = theboard.currplyr.other()
        ccvars = Checks.checkcheck(theboard, theboard.lastmove, clr)
        check, kingpos, checklist = ccvars
        if check and game:
            mate = Checks.matecheck(theboard, kingpos, checklist)
            game = not mate
            if mate:
                print(theboard)
                print(f"Checkmate. {repr(theboard.currplyr)} wins")
                game = False
                break
            else:
                print('Check')
        theboard.currplyr = theboard.currplyr.other()



try:
    with Input() as input_gen:
        with FullscreenWindow() as window:
            main(input_gen, window)
except Checks.PlayerExit:
    pass
