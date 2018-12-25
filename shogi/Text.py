from shogi import Shogi
from shogi import Shogiclasses
import json
import curtsies


def otherconditions(input_gen, window, todisp, theboard, var):
    if var == 'drop':
        droppiece(input_gen, window, todisp, theboard)
        return True
    if var == 'quit':
        toquit(input_gen, window, todisp)
        raise Shogiclasses.IllegalMove(0)
    if var == 'help':
        helpdesk(input_gen, window, theboard)
        raise Shogiclasses.IllegalMove(0)
    if var[:4] == 'help':
        filenm = var[4:]
        filenm = filenm.strip()
        helpdesk(input_gen, window, theboard, filenm)
        raise Shogiclasses.IllegalMove(0)


def droppiece(input_gen, window, todisp, theboard):
    if not theboard.CAPTURED[theboard.currplyr]:
        raise Shogiclasses.IllegalMove(7)
    todisp.append('Enter piece name to put in play')
    todisp.append('> ')
    if moved.startswith('k'):
        moved = 'n'
    try:
        todisp = todisp[:-2]
        thepiece = Shogiclasses.piece(moved[0], theboard.currplyr)
        if thepiece in theboard.CAPTURED[theboard.currplyr]:
            todisp.append('Enter location to place piece')
            todisp.append(': ')
            moveto = getinput(input_gen, window, todisp)
            if Shogi.inputpiece(theboard, moveto):
                moveto = Shogiclasses.coord(moveto)
                theboard.putinplay(thepiece, moveto)
        else:
            raise Shogiclasses.IllegalMove(10)
    except ValueError:
        pass
    except Shogi.OtherInput:
        otherconditions(input_gen, window, todisp, theboard, moveto)


def helpdesk(input_gen, window, theboard, filenm=None):
    todisp = []
    with open('shogihelp.txt') as helpf:
        filetxt = helpf.read()
    if filenm is not None:
        if filenm == 'moves':
            movelistfn(input_gen, window, theboard)
            return
        filenm = ltrtoname(filenm)
        try:
            with open(f"helpfiles/{filenm}.txt") as f:
                thefile = f.read()
            prompt = 'Press Esc to return to game'
            filedisp(input_gen, window, prompt, thefile)
        except FileNotFoundError:
            toout = 'Invalid help command. Type "help" for command list.'
            print(toout)
        return
    prompt = 'Press Esc to activate help menu'
    todisp = filedisp(input_gen, window, prompt, filetxt)
    while True:
        todisp = todisp[:-1]
        todisp.append('help: ')
        filenm = getinput(input_gen, window, todisp)
        filenm = filenm.strip()
        filelwr = filenm.lower()
        if filelwr == 'exit':
            break
        elif filelwr == 'quit':
            toquit(input_gen, window, todisp)
        elif filelwr == 'moves':
            movelistfn(input_gen, window, theboard)
        else:
            filenm = ltrtoname(filenm)
            filenm = filenm.lower()
            try:
                with open(f"helpfiles/{filenm}.txt") as f:
                    thefile = f.read()
                prompt = 'Press Esc to activate help menu'
                todisp = filedisp(input_gen, window, prompt, filetxt)
            except FileNotFoundError:
                print('Invalid help command\n')
                with open("helpfiles/helpcommands.txt") as f:
                    commands = f.read()
                print(commands)


def ltrtoname(filenm):
    with open('datafiles/names.json') as f:
        namedict = json.load(f)
    if filenm.lower() in namedict:
        if filenm.islower():
            filenm = namedict[filenm]
        elif filenm.isupper():
            filenm = '+'+namedict[filenm.lower()]
    return filenm


def setpos(input_gen, window):
    theboard = Shogiclasses.board()
    todict = {}
    while True:
        todisp = []
        todisp.append('Choose location')
        loc = getinput(input_gen, window, todisp)
        loc = loc.strip()
        if loc == 'done':
            todisp.append('Board completed')
            window.render_to_terminal(todisp)
            break
        try:
            valid = Shogi.inputpiece(input_gen, window)
        except Shogi.OtherInput:
            otherconditions(input_gen, window, todisp, theboard, loc)
        if not valid:
            print('Invalid location')
            continue
        loc = Shogiclasses.coord(loc)
        todisp.append('Choose piece and color ')
        pcstr = getinput(input_gen, window, todisp)
        try:
            piecenm = Shogiclasses.piece(*pcstr)
        except (ValueError, IndexError):
            print('Invalid piece\n')
            continue
        todict[loc] = piecenm
    toreturn = Shogiclasses.board(todict)
    return toreturn


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
            raise Shogi.PlayerExit
        else:
            break


def movelistfn(input_gen, window, theboard):
    movedict = {}
    currpieces = theboard.currpcs()
    for loc, apiece in currpieces.items():
        movelst = []
        dirlist = (Shogiclasses.direction(x) for x in range(8))
        for x in dirlist:
            tolst = apiece.validspaces(x)
            tolst = testspcs(theboard, loc, tolst)
            movelst += tolst
        movedict[loc] = movelst
    filestr = ''
    for loc, piece in currpieces.items():
        filestr += f"{repr(piece)} at {loc}:\n"
        toprint = (str(x) for x in movedict[loc])
        filestr += f"    {', '.join(toprint)}\n"
    filestr = filestr.strip()
    prompt = "Press Esc to return to game"
    filedisp(input_gen, window, prompt, filestr)


def testspcs(theboard, pieceloc, spacelist):
    toreturn = []
    for relloc in spacelist:
        try:
            absloc = pieceloc+relloc
            Shogi.movecheck2(theboard, (pieceloc, absloc))
        except (TypeError, ValueError, Shogi.IllegalMove):
            continue
        else:
            toreturn.append(absloc)
    return toreturn


def getinput(input_gen, window, todisp):
    toreturn = ''
    window.render_to_terminal(todisp)
    esccode = 0
    for c in input_gen:
        if esccode:
            esccode -= 1
            continue
        if isinstance(c, curtsies.events.PasteEvent):
            continue
        if c == '<Ctrl-j>':
            break
        elif c == '<BACKSPACE>':
            todisp[-1] = todisp[-1][:-1]
            toreturn = toreturn[:-1]
        elif c.startswith('<'):
            continue
        elif len(c) > 1:
            esccode = 3
            continue
        else:
            todisp[-1] += c
            toreturn += c
        window.render_to_terminal(todisp)
    return toreturn


def yninput(input_gen, window, todisp):
    window.render_to_terminal(todisp)
    for c in input_gen:
        if c == 'y':
            return True
        if c == 'n':
            return False
        window.render_to_terminal(todisp)


def filedisp(input_gen, window, prompt, filetxt):
    maxx = window.width
    maxy = window.height
    filetxt = filetxt.split('\n')
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


def getfile(filenm):
    with open('datafiles/helpindex.json') as f:
        filedict = json.load(f)
    for key, value in filedict['pieces'].items():
        promkey = '+'+key
        if isinstance(value, dict):
            filedict['pieces'][promkey] = filedict['pieces'][key]['promoted']
            filedict['pieces'][key] = filedict['pieces'][key]['unpromoted']
    flatten_dict(filedict)


def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "." + subkey, subvalue
            else:
                yield key, value

    return dict(items())