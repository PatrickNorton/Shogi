from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text as print
import Shogi
import Shogiclasses
import json
def main(session):
    theboard = Shogiclasses.board()
    game = True
    debug = False
    errstr = ''
    if debug:
        theboard = Shogi.setpos(session)
    with open('shogierrors.json') as etxt:
        errorlist = json.load(etxt)
    while game:
        if errstr:
            print('<b>Error: '+errstr+'</b>')
            errstr = ''
        print(str(theboard))
        print(f"{repr(theboard.currplyr)}'s turn")
        try:
            pieceloc = Shogi.piececheck(session, theboard)
            coords = Shogi.movecheck(session, theboard, pieceloc)
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
                topromote = session.prompt('Promote this piece? ')
                topromote = topromote.startswith('y')
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


session = PromptSession()
main(session)