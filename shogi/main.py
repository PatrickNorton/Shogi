from curtsies import FullscreenWindow, Input, fsarray
from curtsies.fmtfuncs import bold
from curtsies.events import PasteEvent
from . import functions
from . import classes
import json


def main(input_gen, window):
    theboard = classes.board()
    game = True
    debug = False
    errstr = ''
    if debug:
        theboard = functions.setpos(input_gen, window)
    errorlist = functions.inputs._geterrors()
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
            pieceloc = functions.getinput(input_gen, window, todisp)
            pieceloc = functions.piececheck(theboard, pieceloc)
            todisp = maindisp[:]
            astr = f"The piece is a {repr(theboard[pieceloc])} at {pieceloc}."
            todisp.append(astr)
            todisp.append('Enter location to move piece to')
            todisp.append(': ')
            moveloc = functions.getinput(input_gen, window, todisp)
            coords = functions.movecheck(theboard, pieceloc, moveloc)
            functions.movecheck2(theboard, coords)
            theboard.nextmove = coords
            tocc = (theboard, theboard.nextmove, theboard.currplyr, True)
            ccvars = functions.checkcheck(*tocc)
            check = ccvars[0]
            if check:
                raise classes.IllegalMove(6)
        except classes.IllegalMove as e:
            var = int(str(e))
            if var:
                errstr = f"Error: {errorlist[var]}"
            continue
        except classes.OtherInput as e:
            pieceloc = e.args[0]
            try:
                functions.otherconditions(
                    input_gen, window, todisp, theboard, pieceloc
                )
            except classes.IllegalMove as e:
                var = int(str(e))
                if var:
                    errstr = f"Error: {errorlist[var]}"
                continue
            except classes.OtherMove:
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
                topromote = functions.yninput(input_gen, window, todisp)
                if topromote:
                    theboard.promote(moveloc)
        theboard.lastmove = theboard.nextmove
        clr = theboard.currplyr.other()
        ccvars = functions.checkcheck(theboard, theboard.lastmove, clr)
        check, kingpos, checklist = ccvars
        if check and game:
            mate = functions.matecheck(theboard, kingpos, checklist)
            game = not mate
            if mate:
                print(theboard)
                print(f"Checkmate. {repr(theboard.currplyr)} wins")
                game = False
                break
            else:
                print('Check')
        theboard.currplyr = theboard.currplyr.other()


def playgame():
    try:
        with Input() as input_gen:
            with FullscreenWindow() as window:
                main(input_gen, window)
    except classes.PlayerExit:
        pass
