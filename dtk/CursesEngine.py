import _curses
import curses
import curses.ascii
import types
import os
import time

from Engine import Engine


class NoInputCharException(Exception):
    pass


class CursesEngine(Engine):
    """
    CursesEngine provides an abstraction of the screen
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


    # this map is used to handle non-printable input characters
    # from the curses module with the keypad(True) method called.
    # in theory input values are meant to be in [0-255], but
    # python's curses module seems to give back some values
    # that are more than one byte, but that might be OK as long
    # as it is consistent.
    
    keymap = { 
               curses.ascii.ESC : "esc",
               curses.ascii.TAB : "tab",
               curses.ascii.NL  : "enter", # regular "return" key
               curses.KEY_ENTER : "enter", # the numpad enter key

               curses.KEY_UP    : "up",
               curses.KEY_DOWN  : "down",
               curses.KEY_LEFT  : "left",
               curses.KEY_RIGHT : "right",

               curses.KEY_HOME  : "home",
               curses.KEY_NPAGE : "page down",
               curses.KEY_PPAGE : "page up",
               curses.KEY_END   : "end",

               curses.KEY_BACKSPACE : "backspace",

               curses.KEY_IC    : "insert",
               curses.KEY_DC    : "delete",
               curses.ascii.DEL : "delete",

               curses.KEY_F1  : "F1",
               curses.KEY_F2  : "F2",
               curses.KEY_F3  : "F3",
               curses.KEY_F4  : "F4",
               curses.KEY_F5  : "F5",
               curses.KEY_F6  : "F6",
               curses.KEY_F7  : "F7",
               curses.KEY_F8  : "F8",
               curses.KEY_F9  : "F9",
               curses.KEY_F10 : "F10",
               curses.KEY_F11 : "F11",
               curses.KEY_F12 : "F12",
               } 



    def __init__(self, *args, **kwargs):
        # some things can only be done once curses.init_scr has been called
        self.cursesInitialized = False
        self.doWhenCursesInitialized = []

        try:
            wantslog = kwargs['wantslog']
        except KeyError:
            wantslog = False
        
        super(CursesEngine, self).__init__(*args, **kwargs)

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

        curses.wrapper(self.cursesMainLoop)


    def cursesMainLoop(self, scr):
        """
        the actual main loop. waits for input and
        does its thing.
        """

        self.scr = scr

        (self.h, self.w) = self.scr.getmaxyx()
        
        self.setTitle(self.title)

        # our terminating condition
        self.done = False

        # ask curses to parse the input for us into
        # single integers at a time
        self.scr.keypad(True)
        
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
        curses.halfdelay(1)

        while not self.done:
            # first try to detect and handle a terminal resize
            (h, w) = self.scr.getmaxyx()

            # update self.resized to be True if the height
            # or width has changed since the last iteration
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

                
            # wait until i say so to update the screen state
            self.scr.noutrefresh()


            # tell children to draw
            self.root.drawContents()

            if len(self.focusStack):
                # draw from the bottom up
                for name in self.focusStack:
                    self.drawables[name].drawContents()


            # draw the cursor if it's valid
            if self.cursorpos == (-1, -1):
                self.scr.move(self.h - 1, self.w - 1)
            else:
                self.scr.move(self.cursorpos[0], self.cursorpos[1])


            curses.doupdate()

            

            # get and parse the input
            #
            # for multi-byte input, this whole section will
            # be called multiple times, which means that
            # parseInput only gets access to one byte of the
            # input at a time, and must maintain its state
            # (ie location in keymap) somehow
            input = self.scr.getch()
            try:
                input = self.parseInput(input)
            except NoInputCharException:
                input = None
                
            # after this, input will be a convenient string
            # such as 'a' or 'space', or None, which means
            # we're waiting on further multi-byte input

            if input is not None:
                drawable = self.getFocusedDrawable()

                # we hand the input off to the focused Drawable,
                # and recurse up the implicit stack until
                # 'drawable' is the Engine. if we haven't gotten
                # a positive acknowledgement that the input was
                # handled, then we try the Engine's bindings
                # as a last resort
                handled = False
                while drawable is not self:
                    handled = drawable.handleInput(input)
                    if handled:
                        break
                    
                    drawable = drawable.getParent()

                if not handled:
                    self.handleInput(input)
                

    def parseInput(self, char):
        """
        if the char is a printable character, we just return it.
        if it's one of the special curses characters (for things
        like arrow keys, combinations, etc) then we will try
        our best to figure out what it was and return that instead.

        Ths method has been ruined by Peter Norton

        Now with logging
        """

        # In half-delay mode with 8-bit (and more! BONUS BITS!)  input
        # python curses' screen.getch() will return -1 to indicate
        # that no key was pressed. It's documented as raising an
        # exception, but I'm happy to get something consistant in this
        # all-too-underdocumented module.
        #
        # XXX report the documentation inconsistancy to get it fixed?
        #
        # -PN
        if char == -1:
            # awwww... heck, raise an exception
            raise NoInputCharException

        # If it's the decimal representation of
        # a printable character... HEY! THAT'S EASY!
        elif curses.ascii.isprint(char):
            self.log.debug("Returning char %s" % chr(char))
            return chr(char)

        # If it's in keymap via a direct lookup, we're golden
        elif char in self.keymap:
            self.log.debug("Returning char %d as %s (curses name %s)", char, self.keymap[char], curses.keyname(char))
            return(self.keymap[char])

        # If we got here, bad user, bad user
        else:
            self.log.info("couldn't parse char: %d" % char)
            # return None
            raise NoInputCharException

    
    def shellMode(self):
        """
        pauses the main loop and returns the terminal to the shell
        mode it was in before starting the Engine. opposite of
        dtkMode()
        """

        # save the program mode
        curses.def_prog_mode()

        self.root.clear()

        # this drops us to shell mode...
        # the next call to curses.refresh() will
        # return to curses mode
        curses.endwin()


    def dtkMode(self):
        """
        returns to dtk mode (from shell mode) and restarts the main
        loop. opposite of shellMode()
        """
        self.touchAll()


    def getScreenSize(self):
        """
        return a tuple (height, width) of the current screen size,
        or (None, None) if curses hasn't been initialized
        """
        if self.cursesInitialized:
            return self.scr.getmaxyx()
        else:
            return (None, None)


    def setTitle(self, title):
        """
        Set the title of the window running DTK, if possible
        """
        Engine.setTitle(self, title)
        print "\033]0;%s\007" % self.title


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
            self.colors[fg] = {}

        if bg not in self.colors[fg].keys():
            curses.init_pair(self.numColors, colormap[fg], colormap[bg])
            self.colors[fg][bg] = curses.color_pair(self.numColors)
            self.numColors += 1

        return self.colors[fg][bg]


    def hideCursor(self):
        """
        hides the cursor, if possible
        """
        self.cursorpos = (-1, -1)


    def touchAll(self):
        """
        causes all drawables to be re-drawn on the next refresh
        """
        for drawable in self.drawables.values():
            drawable.touch()


    def quit(self):
        self.done = True


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
            elif name in self.attrs and attrdict[name] == True:
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
            str = str[:self.w - col]

        if col < 0:
            str = str[-col:]
            col = 0

        # offset the drawable by its origin
        row += drawable.y
        col += drawable.x

        # now draw it
        try:
            self.log.debug('draw: (%d, %d, %s, %d)' % (row, col, str, self.cursesAttr(kwargs)))
            self.scr.addstr(row, col, str, self.cursesAttr(kwargs))
        except _curses.error, e:
            pass


    def _drawDown(self, str, row, col, drawable, **kwargs):
        """
        draws the string at the position given by row and col, with
        the drawing style defined by arguments given in **kwargs.
        these will often include things like face attributes (bold,
        underline, etc), colors, and other things specific to the
        Engine. capabilities() should list all the possibilities.
        """

        if row > drawable.h or col < 0 or col > drawable.w:
            return

        attr = self.cursesAttr(kwargs)

        row += drawable.y

        for char, r in zip(str, range(row, min(drawable.y + drawable.h, self.h))):
            self.scr.addstr(r, col, char, attr)


        
    def _box(self, x, y, w, h, drawable, **kwargs):
        """
        draws a line using border characters appropriate to the 
        underlying technology, starting at the location given by
        (x, y) with the given width and height. fails silently if
        any part of the box is to be drawn is outside the area
        allowed by the drawable.
        """

        # check bounds
        if x < 0 or y < 0 or x + w > drawable.w or y + h > drawable.h:
            return

        x += drawable.x
        y += drawable.y

        attr = self.cursesAttr(kwargs)

        # draw corners
        self.scr.addch(y, x, curses.ACS_ULCORNER, attr)
        self.scr.addch(y, x + w - 1, curses.ACS_URCORNER, attr)
        self.scr.addch(y + h - 1, x, curses.ACS_LLCORNER, attr)
        try:
            self.scr.addch(y + h - 1, x + w - 1, curses.ACS_LRCORNER, attr)
        except _curses.error, e:
            pass

        # draw edges
        if attr:
            # if we have an attribute, we have to draw char-by-char
            for r in range(x + 1, x + w - 1):
                self.scr.addch(y, r, curses.ACS_HLINE, attr)
                self.scr.addch(y + h - 1, r, curses.ACS_HLINE, attr)
    
            for c in range(y + 1, y + h - 1):
                self.scr.addch(c, x, curses.ACS_VLINE, attr)
                self.scr.addch(c, x + w - 1, curses.ACS_VLINE, attr)

        else:
            # else we can use these functions which are probably quicker
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
                        self.log.debug("exception at (%d, %d)" % (r, c))
                        raise e

    def _showCursor(self, y, x, drawable):
        """
        draws a "cursor" to the given screen position, or none at all
        if (x, y) is outside the area allowed for the drawable
        """
        if x < 0 or x > drawable.w or y < 0 or y > drawable.h:
            self.cursorpos = (-1, -1)
        else:
            self.cursorpos = (drawable.y + y, drawable.x + x)

