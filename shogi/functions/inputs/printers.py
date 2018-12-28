__all__ = [
    "filedisp"
]

def filedisp(input_gen, window, prompt, filetxt):
    """Print a file to screen.
    
    Arguments:
        input_gen {curtsies.Input} -- input generator
        window {curtsies.FullScreenWindow} -- window to print text
        prompt {str} -- prompt to print at bottom of screen
        filetxt {text} -- text of file in question
    
    Returns:
        list -- current screen contents
    """

    maxx = window.width
    maxy = window.height
    filetxt = filetxt.splitlines()
    filelist = []
    for lin in filetxt:
        if len(lin) >= maxx-1:
            filelist.append(lin[:maxx-1])
            filelist.append(lin[:maxx-1])
        else:
            filelist.append(lin)
    scrollable = True
    while len(filelist) < maxy-2:
        scrollable = False
        filelist.append('')
    firstline = 0
    todisp = filetxt[:maxy-2]
    todisp.append(prompt)
    window.render_to_terminal(todisp)
    for c in input_gen:
        if scrollable:
            if c == '<UP>':
                if firstline > 0:
                    firstline -= 1
            if c == '<DOWN>':
                if firstline+maxy-2 < len(filelist):
                    firstline += 1
        if c == '<ESC>':
            break
        todisp = filetxt[firstline:firstline+maxy-2]
        todisp.append(prompt)
        window.render_to_terminal(todisp)
    return todisp
