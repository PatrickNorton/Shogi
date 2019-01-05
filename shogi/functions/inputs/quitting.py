from shogi.functions import classes

__all__ = [
    "toquit"
]


def toquit(input_gen, window, todisp):
    """Check if player wants to quit.

    Depreciated: use .oddinputs.may_quit() instead

    Arguments:
        input_gen {curtsies.Input} -- input generator
        window {curtsies.FullScreenWindow} -- window to print text
        todisp {list} -- list of current screen content

    Raises:
        classes.PlayerExit -- player wishes to exit
    """

    while True:
        todisp.append('You are about to quit the game of Shogi')
        todisp.append('Are you sure you want to quit?')
        window.render_to_terminal(todisp)
        for c in input_gen:
            if c == 'y':
                toquit = True
                break
            elif c == 'n':
                toquit = False
                break
        if toquit:
            raise classes.PlayerExit
        else:
            break
