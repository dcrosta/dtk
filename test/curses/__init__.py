import time

# a unittest-worthy replacement for python's curses module,
# at least as far as DTK is concerned

# term attributes
A_BOLD = 1
A_REVERSE = 2
A_NORMAL = 4
A_BLINK = 8
A_DIM = 16
A_STANDOUT = 32
A_UNDERLINE = 64


# key codes (more in ascii.py)
KEY_ENTER = 'enter'

KEY_UP = 'up'
KEY_DOWN = 'down'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'

KEY_HOME = 'home'
KEY_NPAGE = 'page down'
KEY_PPAGE = 'page up'
KEY_END = 'end'

KEY_BACKSPACE = 'backspace'

KEY_IC = 'insert'
KEY_DC = 'delete'

KEY_F1 = 'F1'
KEY_F2 = 'F2'
KEY_F3 = 'F3'
KEY_F4 = 'F4'
KEY_F5 = 'F5'
KEY_F6 = 'F6'
KEY_F7 = 'F7'
KEY_F8 = 'F8'
KEY_F9 = 'F9'
KEY_F10 = 'F10'
KEY_F11 = 'F11'
KEY_F12 = 'F12'

COLOR_WHITE = 'white'
COLOR_BLACK = 'black'
COLOR_BLUE = 'blue'
COLOR_CYAN = 'cyan'
COLOR_GREEN = 'green'
COLOR_MAGENTA = 'magenta'
COLOR_RED = 'red'
COLOR_YELLOW = 'yellow'

# symbol-thingies
ACS_ULCORNER = ACS_URCORNER = ACS_LLCORNER = ACS_LRCORNER = '+'
ACS_VLINE = '|'
ACS_HLINE = '-'
ACS_TTEE = ACS_BTEE = '+'


def make_buf(y, x):
    buf = list()
    for i in xrange(y):
        line = list()
        for j in xrange(x):
            line.append(' ')
        buf.append(line)
    return buf


class Screen:

    def __init__(self, y, x):
        self._maxyx = (y, x)
        self._keypad = False
        self._cursor = (0, 0)
        self._screen = make_buf( *list(self.getmaxyx()) )

    def getmaxyx(self):
        return self._maxyx

    def keypad(self, val):
        self.keypad = val

    def move(self, y, x):
        self._cursor = (y, x)

    def clrtobot(self):
        y, x = self._cursor
        my, mx = self.getmaxyx()

        for i in xrange(y, my):
            for j in xrange(x, mx):
                self._screen[i][j] = ' '

    def _addstr(self, s):
        y, x = self._cursor
        my, mx = self.getmaxyx()

        for ltr in s:
            self._screen[y][x] = ltr

            x += 1
            if x >= mx:
                x = 0
                y += 1
            if y >= my:
                print "out of bounds: (%d, %d)" % (y, x)

        self._cursor = (y, x)

    def addstr(self, *args):
        if len(args) == 1:
            self._addstr(args[0])
        elif len(args) == 2:
            self._addstr(args[0])
        elif len(args) == 3:
            y, x, s = args
            self.move(y,x)
            self._addstr(s)
        elif len(args) == 4:
            y, x, s, attr = args
            self.move(y,x)
            self._addstr(s)
        else:
            raise "addstr called with %d arguments" % len(args)

    addch = addstr

    def hline(self, *args):
        if len(args) == 2:
            ch, n = args
            self.addstr( ch * int(n) )
        elif len(args) == 4:
            y, x, ch, n = args
            self.addstr( y, x, ch * int(n) )

    def _vline(self, ch, n):
        y, x = self._cursor
        my, mx = self.getmaxyx()

        for i in xrange(n):
            self._screen[y][x] = ch

            y += 1
            if y >= my:
                print "out of bounds: (%d, %d)" % (y, x)

    def vline(self, *args):
        if len(args) == 2:
            self._vline( *args )
        elif len(args) == 4:
            y, x, ch, n = args
            self.move( y, x )
            self._vline( ch, n )


    def getch(self):
        global _halfdelay, _ticks
        delay = _halfdelay
        if _halfdelay is None:
            delay = 10.0
        delay = float(delay) / 10.0
        _ticks += delay
        time.sleep( delay )


    def __str__(self):
        out = ''
        out += '-' * (_scr.getmaxyx()[1]+2)
        out += '\n'
        for line in _scr._screen:
            out += "|%s|\n" % (''.join(line))

        out += '-' * (_scr.getmaxyx()[1]+2)

        return out

    def noop(self, *args, **kwargs):
        pass

    refresh = noop
    noutrefresh = noop
    doupdate = noop

_halfdelay = None
def halfdelay(ticks):
    global _halfdelay
    _halfdelay = ticks

_colors = []
def start_color():
    pass

def tigetstr(*args):
    return None

def doupdate():
    global _scr, _start, _ticks

    print round( 10.0 * (_ticks - _start) ) / 10.0
    print _scr
    print "\n"


_scr = None
_start = 0
_ticks = 0
def wrapper(callback):
    global _scr
    _scr = Screen(24,80)

    callback(_scr)
