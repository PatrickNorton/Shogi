from curtsies import FullscreenWindow, Input, fsarray
from curtsies.fmtfuncs import bold
from curtsies.events import PasteEvent
from pyfiles import Shogi
from pyfiles import Shogiclasses
from pyfiles import Shogitxt
import json


def main(input_gen, window):
    theboard = Shogiclasses.board()
    game = True
    debug = False
    errstr = ''
    if debug:
        theboard = Shogitxt.setpos(input_gen, window)
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
            pieceloc = Shogitxt.getinput(input_gen, window, todisp)
            pieceloc = Shogi.piececheck(theboard, pieceloc)
            todisp = maindisp[:]
            astr = f"The piece is a {repr(theboard[pieceloc])} at {pieceloc}."
            todisp.append(astr)
            todisp.append('Enter location to move piece to')
            todisp.append(': ')
            moveloc = Shogitxt.getinput(input_gen, window, todisp)
            coords = Shogi.movecheck(theboard, pieceloc, moveloc)
            Shogi.movecheck2(theboard, coords)
            theboard.nextmove = coords
            tocc = (theboard, theboard.nextmove, theboard.currplyr, True)
            ccvars = Shogi.checkcheck(*tocc)
            check = ccvars[0]
            if check:
                raise Shogiclasses.IllegalMove(6)
        except Shogiclasses.IllegalMove as e:
            var = int(str(e))
            if var:
                errstr = f"Error: {errorlist[var]}"
            continue
        except Shogi.OtherInput as e:
            pieceloc = e.args[0]
            Shogitxt.otherconditions(
                input_gen, window, todisp, theboard, pieceloc
                )
        except Shogi.OtherMove:
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
                topromote = Shogitxt.yninput(input_gen, window, todisp)
                if topromote:
                    theboard.promote(moveloc)
        theboard.lastmove = theboard.nextmove
        clr = theboard.currplyr.other()
        ccvars = Shogi.checkcheck(theboard, theboard.lastmove, clr)
        check, kingpos, checklist = ccvars
        if check and game:
            mate = Shogi.matecheck(theboard, kingpos, checklist)
            game = not mate
            if mate:
                print(theboard)
                print(f"Checkmate. {repr(theboard.currplyr)} wins")
                game = False
                break
            else:
                print('Check')
        theboard.currplyr = theboard.currplyr.other()




with Input() as input_gen:
    with FullscreenWindow() as window:
        main(input_gen, window)
