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
        theboard = functions.setup_board(input_gen, window)
    while game:
        todisp = []
        if errstr:
            todisp.append(bold(errstr))
            errstr = ''
        todisp += str(theboard).split('\n')
        todisp.append(f"{theboard.current_player !r}'s turn")
        maindisp = todisp[:]
        todisp.append('Enter piece location')
        todisp.append(': ')
        try:
            pieceloc = functions.get_input(input_gen, window, todisp)
            pieceloc = functions.piece_check(theboard, pieceloc)
            todisp = maindisp[:]
            astr = f"The piece is a {theboard[pieceloc] !r} at {pieceloc}."
            todisp.append(astr)
            todisp.append('Enter location to move piece to')
            todisp.append(': ')
            moveloc = functions.get_input(input_gen, window, todisp)
            coords = functions.move_check(pieceloc, moveloc)
            functions.move_check_2(theboard, coords)
            theboard.next_move = coords
            tocc = (theboard, theboard.next_move, theboard.current_player, True)
            ccvars = functions.check_check(*tocc)
            checklist = ccvars[1]
            if checklist:
                raise classes.IllegalMove(6)
        except classes.IllegalMove as e:
            var = int(e)
            if var:
                errstr = f"Error: {e}"
            continue
        except classes.OtherInput as e:
            pieceloc = e.args[0]
            try:
                functions.other_conditions(
                    input_gen, window, todisp, theboard, pieceloc
                )
            except classes.IllegalMove as f:
                var = int(f)
                if var:
                    errstr = f"Error: {f}"
                continue
            except classes.OtherMove:
                theboard.current_player = theboard.current_player.other
                continue
        theboard.move(*theboard.next_move)
        moveloc = theboard.next_move[1]
        promote = theboard.can_promote(moveloc)
        canpromote = theboard[moveloc].is_promotable
        ispromoted = theboard[moveloc].prom
        if promote and canpromote and not ispromoted:
            if theboard.auto_promote(moveloc):
                theboard.promote(moveloc)
            else:
                todisp.append('Promote this piece? ')
                topromote = functions.binary_input(input_gen, window, todisp)
                if topromote:
                    theboard.promote(moveloc)
        theboard.last_move = theboard.next_move
        clr = theboard.current_player.other
        ccvars = functions.check_check(theboard, theboard.last_move, clr)
        kingpos, checklist = ccvars
        if checklist and game:
            mate = functions.mate_check(theboard, kingpos, checklist)
            game = not mate
            if mate:
                print(theboard)
                print(f"Checkmate. {theboard.current_player !r} wins")
                game = False
                break
            else:
                print('Check')
        theboard.current_player = theboard.current_player.other


def playgame():
    """Context manager for main()."""

    try:
        with Input() as input_gen:
            with FullscreenWindow() as window:
                main(input_gen, window)
    except classes.PlayerExit:
        pass
