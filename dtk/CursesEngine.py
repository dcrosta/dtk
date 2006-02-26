import _curses
import curses
import curses.ascii
import types
import os
import time

from Engine import Engine



class CursesEngine(Engine):
    """
    CursesEngine provides a character buffer of the screen
    implemented using the python curses module. It creates
    one curses.win object (through curses.wrapper()) and uses
    its own logic to determine occlusion, etc, for everything
    else.
    """

    # attributes for drawing
    attrs = {
        'bold':curses.A_BOLD,
        'highlight':curses.A_REVERSE,
        'normal':curses.A_NORMAL,
        'blink':curses.A_BLINK,
        'dim':curses.A_DIM,
        'bright':curses.A_STANDOUT,
        'underline':curses.A_UNDERLINE
        }

    colors = None


    # since we handle complicated (non-printable) input
    # by getting a series of 7-bit characters from curses,
    # we can use a nested dictionary to look up various
    # keycode sequences to see if they are valid input
    # tokens or not.
    keymap = { 9   : "tab",
               10  : "enter",
               27  : { 79 : { 77 : "enter",
                              80 : "F1",
                              81 : "F2",
                              82 : "F3",
                              83 : "F4",
                              109: "-",
                              107: "+"},
                      None: "esc", # if we get a 27, followed by nothing,
                                   # it's an ESC
                      91  : { 49  : { 49  :  { 126 : "F1"},
                                      50  : { 126 : "F2"},
                                      51  : { 126 : "F3"},
                                      52  : { 126 : "F4"},
                                      53  : { 126 : "F5"},
                                      55  : { 126 : "F6" },
                                      56  : { 126 : "F7" },
                                      57  : { 126 : "F8" },
                                      126 : "home" },
                              50  : { 48  : { 126 : "F9" },
                                      49  : { 126 : "F10" },
                                      51  : { 126 : "F11" },
                                      52  : { 126 : "F12" },
                                      126 : "insert" },
                              51  : { 126 : "delete" },
                              52  : { 126 : "end" },
                              53  : { 126 : "page up" },
                              54  : { 126 : "page down" },
                              55  : { 126 : "home" },
                              56  : { 126 : "end" },
                              65  : "up",
                              66  : "down",
                              67  : "right",
                              68  : "left",
                              70  : "end",
                              72  : "home",
                              90  : "tab",
                              91  : { 65  : "F1",
                                      66  : "F2",
                                      67  : "F3",
                                      68  : "F4",
                                      69  : "F5" } } },
               32  : "space",
               127 : "backspace",

               # occasionally (though maybe not any more, or not
               # on all systems) we get non-7 bit inputs... so
               # we handle them just in case
               258 : "down",
               259 : "up",
               260 : "left",
               261 : "right",
               265 : "F1",
               266 : "F2",
               267 : "F3",
               268 : "F4",
               269 : "F5",
               270 : "F6",
               271 : "F7",
               272 : "F8",
               273 : "F9",
               274 : "F10",
               275 : "F11",
               276 : "F12",
               330 : "delete",
               331 : "insert",
               338 : "page down",
               339 : "page up",
               } 



    class Character:
        """
        the basic unit that goes into the screen buffer.
        Character wraps the notion of a single printable
        letter string with a curses attribute string and
        a flag to indicate that the character has changed
        and must be redrawn
        """

        def __init__(self, char, attr, engine):
            self.char = char
            self.attr = attr
            self.diff = True # initially, draw everything

        def __str__(self):
            return self.char


    def __init__(self, *args, **kwargs):
        # some things can only be done once curses.init_scr has been called
        self.cursesInitialized = False
        self.doWhenCursesInitialized = []

        Engine.__init__(self, *args, **kwargs)

        # eventually, a list of lists of Characters
        self.buffer = []

        # initially, we are tiny!
        self.w = 0
        self.h = 0
        self.resized = True

        # cursor position
        self.cursorpos = (-1, -1)

        # for input handling
        self.curmap = self.keymap


    def mainLoop(self):
        """
        initializes curses, and asks it to run the
        actual main event loop function
        """

        # this code adapted from curses.wrapper
        try:
            self.scr = curses.initscr()

            # save the shell mode so we can drop back into it later.
            curses.def_shell_mode()

            curses.noecho()
            curses.cbreak()

            return self.cursesMainLoop(self.scr)
        finally:
            curses.echo()
            curses.nocbreak()
            curses.endwin()


    def cursesMainLoop(self, scr):
        """
        the actual main loop. waits for input and
        does its thing.
        """

        # self.scr = scr

        self.initBuffer()
        
        # set terminal name string
        print "\033]0;%s\007" % self.name

        # our terminating condition
        self.done = False

        # this ensures that we always get things as multi-character
        # input for special keys (arrows, etc)...
        self.scr.keypad(False)
        
        # this doesn't always work in all terms, but will never
        # fail in such a way as to break anything. by default
        # we want to hide it to keep the GUI pretty
        self.hideCursor()

        # here we do anything we decided could only be done
        # after curses is initialized
        self.cursesInitialized = True
        for foo in self.doWhenCursesInitialized:
            if type(foo) == types.TupleType:
                (method, kwargs) = foo

                method(**kwargs)
            else:
                foo()


        # these are all 0 so that we get a "resize" on the first time
        # h = w = lasth = lastw = 0
        self.resized = True

        # handle input every 1/10th of a second
        #
        # this is necessary to handle input of (possibly
        # among others) 'esc'
        curses.halfdelay(2)

        while not self.done:
            # first try to detect and handle a terminal resize
            (h, w) = self.scr.getmaxyx()

            # update self.resized to be True if the height
            # or width has changed since the last iteration
            if self.resized:
                self.log('self.resized: True')

            self.resized = self.resized or h != lasth or w != lastw

            if self.resized:
                # a resize has happened
                self.root.setSize(0, 0, h, w)
                
                lasth = h
                lastw = w
                self.resized = False

                # try to erase everything (necessary in some terms)
                self.scr.move(0,0)
                self.scr.clrtobot()
                self.scr.refresh()

                # XXX: minor hack!
                self.showCursor()
                self.hideCursor()
                
            # wait until i say so to update the screen state
            self.scr.noutrefresh()

            # tell children to draw to the buffer
            self.root.drawContents()

            # draw the cursor if it's valid
            if self.cursorpos != (-1, -1):
                self.showCursor()
                self.scr.move(self.cursorpos[0], self.cursorpos[1])
            else:
                self.hideCursor()

            curses.doupdate()

            

            # get and parse the input
            #
            # for multi-byte input, this whole section will
            # be called multiple times, which means that
            # parseInput only gets access to one byte of the
            # input at a time, and must maintain its state
            # (ie location in keymap) somehow
            input = self.scr.getch()
            input = self.parseInput(input)

            # after this, input will be a convenient string
            # such as 'a' or 'space', or None, which means
            # we're waiting on further multi-byte input

            if input is not None:
                drawable = self.getFocusedDrawable()

                # we hand the input off to the focused Drawable,
                # and recurse up the implicit stack until
                # drawable is the Engine
                while drawable is not self:
                    if drawable.handleInput(input):
                        break
                    else:
                        drawable = drawable.getParent()
                

    def parseInput(self, char):
        """
        if the char is a printable character, we just return it.
        if it's one of the special curses characters (for things
        like arrow keys, combinations, etc) then we will try
        our best to figure out what it was and return that instead.
        """

        # if we use half-delay mode (where curses blocks only for
        # a short time on getch()) then we get -1 as the return
        # from getch(), and that indicates that we should reset
        # the state for parseInput()
        if char == -1:
            try:
                # 'esc', and possibly others, use chars that are
                # prefixes of other non-printable chars (ugh), so
                # we check that here first
                char = self.curmap[None]
            except KeyError:
                char = None

            # reset things
            self.curmap = self.keymap

            return char

        # otherwise, we look for the char in self.curmap,
        # which always corresponds to one of the nested
        # dictionaries in self.keymap. if we find the char
        # in the curmap, then we either return the friendly
        # string representation if it's a "leaf" of the nested
        # dict data structure, or update curmap to point to
        # the new dictionary if it's an internal point, and
        # return None
        if char in self.curmap.keys():
            if type(self.curmap[char]) == types.DictType:
                self.curmap = self.curmap[char]
                return None
            else:
                char = self.curmap[char]
                self.curmap = self.keymap
                return char

        elif curses.ascii.isprint(char):
            # in case we screwed something up...
            self.curmap = self.keymap

            return chr(char)

        else:
            self.log("couldn't parse char: %d" % char)
            return None
    
    def shellMode(self):
        """
        pauses the main loop and returns the terminal to the shell
        mode it was in before starting the Engine. opposite of
        shellMode()
        """

        # first backup the state of self.scr
        self.winstate = os.tmpfile()
        self.scr.putwin(self.winstate)

        # save the program mode
        curses.def_prog_mode()

        # clean the terminal
        self.scr.move(0, 0)
        self.scr.clrtobot()
        self.scr.refresh()

        time.sleep(1) 

        # and finally drop to shell mode
        curses.echo()
        curses.nocbreak()
        curses.nl()

        # curses.reset_shell_mode()

        curses.endwin()


    def dtkMode(self):
        """
        returns to dtk mode (from shell mode) and restarts the main
        loop. opposite of shellMode()
        """

        return self.mainLoop()

        # self.winstate.seek(0)
        # self.scr = curses.getwin(self.winstate)
        # self.winstate.close()
        # del self.winstate


    def resize(self):
        """
        tells the engine that a resize has happened or that it
        should believe that one has happened and resize all the
        visible Drawables
        """
        self.resized = True
    

    def lookupColorPair(self, fg, bg):
        """
        initialize curses colors, adds appropriate
        constants to self.attrs
        """

        fg = fg.lower()
        bg = bg.lower()

        if self.colors is None:
            curses.start_color()
            self.colors = {}
            self.numColors = 1 # 0 is reserved

        try:
            curses.use_default_colors()
            clearColor = -1
        except:
            clearColor = curses.COLOR_BLACK

        # white on black is the default color, which is pre-defined
        # and can't be overwritten
        if fg == 'white' and (bg == 'black' or bg == 'clear'):
            return 0

        colormap = {
            'white':curses.COLOR_WHITE,
            'black':curses.COLOR_BLACK,
            'blue':curses.COLOR_BLUE,
            'cyan':curses.COLOR_CYAN,
            'green':curses.COLOR_GREEN,
            'magenta':curses.COLOR_MAGENTA,
            'red':curses.COLOR_RED,
            'yellow':curses.COLOR_YELLOW,
            'clear':clearColor
            }

        # otherwise, we first check if the requested
        # color pair exists in our cache of colors, and
        # either return it, or create it and then return it
        if fg not in self.colors.keys():
            self.log("adding '%s' to self.colors" % fg)
            self.colors[fg] = {}

        if bg not in self.colors[fg].keys():
            self.log("adding '%s' to self.colors['%s']" % (bg, fg))
            curses.init_pair(self.numColors, colormap[fg], colormap[bg])
            self.colors[fg][bg] = curses.color_pair(self.numColors)
            self.numColors += 1

        return self.colors[fg][bg]


    def hideCursor(self):
        """
        hides the cursor, if possible
        """
        if self.cursesInitialized:
            if curses.tigetstr('civis') is not None:
                curses.curs_set(0)
        else:
            self.doWhenCursesInitialized.append(self.hideCursor)

    def showCursor(self):
        """
        shows the cursor, if it's hidden
        """
        if self.cursesInitialized:
            if curses.tigetstr('cnorm') is not None:
                curses.curs_set(1)
        else:
            self.doWhenCursesInitialized.append(self.showCursor)


    def quit(self):
        self.done = True


    def initBuffer(self):
        """
        initialize the buffer to all blank spaces
        """
        (self.h, self.w) = self.scr.getmaxyx()

        buffer = []
        for r in range(self.h):
            row = []
            for c in range(self.w):
                row.append(self.Character(' ', 0, self))
            buffer.append(row)

        self.buffer = buffer

    def cursesAttr(self, attrdict):
        """
        calculate the attribute bitstring for curses drawing
        """

        attr = 0

        fg = 'white'
        bg = 'black'

        for name in attrdict.keys():
            if name == 'foreground' or name == 'fg':
                fg = attrdict[name]
            elif name == 'background' or name == 'bg':
                bg = attrdict[name]
            elif name in self.attrs:
                attr |= self.attrs[name]

        attr |= self.lookupColorPair(fg, bg)

        return attr


    def _draw(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the given row and column,
        relative to the drawing area for the drawable, with
        the drawing style defined in **kwargs. if drawing
        should continue out of the area the drawable is allowed
        to draw in, it will be clipped
        """

        # if it's completely off-screen, don't draw
        if row < 0 or row > self.h or col > self.w:
            return

        # truncate the string to fit
        if col + len(str) > drawable.w:
            self.log("clipping str from length %d" % len(str))
            str = str[:self.w - col]
            self.log("               to length %d" % len(str))

        if col < 0:
            str = str[-col:]
            col = 0

        # offset the drawable by its origin
        row += drawable.y
        col += drawable.x

        # now draw it
        try:
            self.scr.addstr(row, col, str, self.cursesAttr(kwargs))
        except _curses.error, e:
            pass

        
    def _box(self, x, y, w, h, drawable, **kwargs):
        """
        draws a line using border characters appropriate to the 
        underlying technology, starting at the location given by
        (x, y) with the given width and height. fails silently if
        any part of the box is to be drawn is outside the area
        allowed by the drawable.
        """

        # check bounds
        if x < drawable.x or y < drawable.y or x + w > drawable.w or y + h > drawable.h:
            return

        x += drawable.x
        y += drawable.y

        attr = self.cursesAttr(kwargs)

        self.scr.addch(y, x, curses.ACS_ULCORNER, attr)
        self.scr.addch(y, x + w - 1, curses.ACS_URCORNER, attr)
        self.scr.addch(y + h - 1, x, curses.ACS_LLCORNER, attr)
        try:
            self.scr.addch(y + h - 1, x + w - 1, curses.ACS_LRCORNER, attr)
        except _curses.error, e:
            pass

        if attr:
            for r in range(x + 1, x + w - 1):
                self.scr.addch(y, r, curses.ACS_HLINE, attr)
                self.scr.addch(y + h - 1, r, curses.ACS_HLINE, attr)
    
            for c in range(y + 1, y + h - 1):
                self.scr.addch(c, x, curses.ACS_VLINE, attr)
                self.scr.addch(c, x + w - 1, curses.ACS_VLINE, attr)
        else:
            self.scr.hline(y, x + 1, curses.ACS_HLINE, w - 2)
            self.scr.hline(y + h - 1, x + 1, curses.ACS_HLINE, w - 2)

            self.scr.vline(y + 1, x, curses.ACS_VLINE, h - 2)
            self.scr.vline(y + 1, x + w - 1, curses.ACS_VLINE, h - 2)


    def _line(self, x, y, len, drawable, **kwargs):
        """
        draws a line starting at (x, y) and going across for
        len cells. ending characters may be specified with the
        leftEnd and rightEnd attributes. line is clipped to
        the available area.
        """

        # invisible line
        if y < 0 or y > drawable.h:
            return

        if x < 0:
            len += x
            x = 0
        if x + len > drawable.w:
            len -= (drawable.w - len)

        x += drawable.x
        y += drawable.y

        attr = self.cursesAttr(kwargs)

        if 'leftEnd' in kwargs:
            self.scr.addch(y, x, kwargs['leftEnd'], attr)
            len -= 1
            x += 1

        if 'rightEnd' in kwargs:
            self.scr.addch(y, x + len - 1, kwargs['rightEnd'], attr)
            len -= 1

        if attr:
            for c in range(x, x + len):
                self.scr.addch(y, c, curses.ACS_HLINE, attr)
        else:
            self.scr.hline(y, x, curses.ACS_HLINE, len)



    def _lineDown(self, x, y, len, drawable, **kwargs):
        """
        draws a line starting at (x, y) and going down for
        len cells. ending characters may be specified with the
        topEnd and bottomEnd attributes. line is clipped to
        the available area.
        """

        # invisible line
        if x < 0 or x > drawable.w:
            return

        if y < 0:
            len += y
            y = 0
        if y + len > drawable.h:
            len -= (drawable.h - len)

        x += drawable.x
        y += drawable.y

        attr = self.cursesAttr(kwargs)

        if 'topEnd' in kwargs:
            self.scr.addch(y, x, kwargs['topEnd'], attr)
            len -= 1
            y += 1

        if 'bottomEnd' in kwargs:
            self.scr.addch(y + len - 1, x, kwargs['bottomEnd'], attr)
            len -= 1

        if attr:
            for r in range(y, y + len):
                self.scr.addch(r, x, curses.ACS_VLINE, attr)
        else:
            self.scr.vline(y, x, curses.ACS_VLINE, len)


    def _clear(self, drawable):
        """
        clears the whole drawable
        """

        for r in range(drawable.y, drawable.y + drawable.h):
            for c in range(drawable.x, drawable.x + drawable.w):
                try:
                    self.scr.addch(r, c, ' ')
                except _curses.error, e:
                    if r == drawable.y + drawable.h - 1 and c == drawable.x + drawable.w - 1:
                        pass
                    else:
                        self.log("exception at (%d, %d)" % (r, c))
                        raise e

    def _showCursor(self, y, x, drawable):
        """
        draws a "cursor" to the given screen position, or none at all
        if (x, y) is outside the area allowed for the drawable
        """
        if  x - drawable.x < 0 or x - drawable.x > drawable.w or y - drawable.y < 0 or y - drawable.y > drawable.h:
            self.cursorpos = (-1, -1)
        else:
            self.cursorpos = (drawable.y + y, drawable.x + x)
