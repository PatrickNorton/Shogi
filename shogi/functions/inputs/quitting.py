from shogi import functions

__all__ = [
    "toquit"
]

def toquit(input_gen, window, todisp):
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
            raise functions.PlayerExit
        else:
            break
