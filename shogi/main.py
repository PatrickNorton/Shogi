from curtsies import FullscreenWindow, Input
from curtsies.fmtfuncs import bold
from . import functions
from . import classes


def main(input_gen: Input, window: FullscreenWindow):
    """Play a complete game of Shogi.

    This uses a window to completely cover the screen, leaving no
    trace on exit. *! IMPORTANT: Do Not Use VSCode's "terminate", but
    use Ctrl-C or type "quit" to end program execution. !* For help
    playing the game, type "help" at a the prompt.

    Arguments:
        input_gen {curtsies.Input} -- for collecting inputs
        window {curtsies.FullScreenWindow} -- for displaying the game

    Raises:
        classes.IllegalMove -- when an illegal move is called
        **Should always be handled within the function
    """

    theboard = classes.Board()
    game = True
    debug = False
    errstr = ''
    if debug:
        theboard = functions.setpos(input_gen, window)
    errorlist = classes.info.ERRORS
    while game:
        todisp = []
        if errstr:
            todisp.append(bold(errstr))
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
                theboard.currplyr = theboard.currplyr.other
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
        clr = theboard.currplyr.other
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
        theboard.currplyr = theboard.currplyr.other


def playgame():
    """Context manager for main()."""

    try:
        with Input() as input_gen:
            with FullscreenWindow() as window:
                main(input_gen, window)
    except classes.PlayerExit:
        pass
