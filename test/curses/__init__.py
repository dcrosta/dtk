import time
import re

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

def keyname(ch):
    return ch

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


# thanks to http://simonwillison.net/2004/Jan/28/sequenceInReverse/
# for the hint on reverse iteration w/out resorting the sequence
class ReverseIterator:
    def __init__(self, sequence):
        self.sequence = sequence

    def __iter__(self):
        length = len(self.sequence)
        i = length
        while i > 0:
            i = i - 1
            yield self.sequence[i]

class Char:
    """
    represents a character on screen, and all the previous
    characters at that location over time
    """

    def __init__(self, ch, time=0):
        self.prev = [(ch, time)]

    def __str__(self):
        return self.prev[len(self.prev)-1][0]

    def set(self, ch, time):
        if self.prev[len(self.prev)-1][1] == time:
            self.prev[len(self.prev)-1] = (ch, time)
        else:
            self.prev.append((ch, time))

    def at(self, time):
        """
        find the character at this position at the given time
        """
        r = ReverseIterator(self.prev)
        for ch, tick in r:
            if tick < time:
                return ch


def make_buf(y, x):
    buf = list()
    for i in xrange(y):
        line = list()
        for j in xrange(x):
            line.append(Char(' '))
        buf.append(line)
    return buf

class Screen:

    def __init__(self, y, x):
        self._maxyx = (y, x)
        self._keypad = False
        self._cursor = (0, 0)
        self._screen = make_buf( *list(self.getmaxyx()) )

        self._input_buf = list()

    def getmaxyx(self):
        return self._maxyx

    def keypad(self, val):
        self.keypad = val

    def move(self, y, x):
        self._cursor = (y, x)

    def clrtobot(self):
        global _ticks

        y, x = self._cursor
        my, mx = self.getmaxyx()

        for i in xrange(y, my):
            for j in xrange(x, mx):
                self._screen[i][j].set(' ', _ticks)

    def _addstr(self, s):
        global _ticks

        y, x = self._cursor
        my, mx = self.getmaxyx()

        for ltr in s:
            if x >= mx:
                x = 0
                y += 1
            if y >= my:
                print "out of bounds: (%d, %d)" % (y, x)

            self._screen[y][x].set(ltr, _ticks)
            x += 1

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
        global _ticks

        y, x = self._cursor
        my, mx = self.getmaxyx()

        for i in xrange(n):
            self._screen[y][x].set(ch, _ticks)

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
        global _halfdelay, _ticks, _use_delay

        _ticks += 1

        if _use_delay:
            delay = _halfdelay / 10.0
            time.sleep( delay )

        if len(self._input_buf) > 0:
            ch = self._input_buf[0]
            self._input_buf = self._input_buf[1:]

            return ch
        else:
            return None


    def __str__(self):
        out = ''
        out += '-' * (self.getmaxyx()[1]+2)
        out += '\n'
        for line in self._screen:
            out += "|%s|\n" % (''.join([str(x) for x in line]))

        out += '-' * (self.getmaxyx()[1]+2)

        return out

    def noop(self, *args, **kwargs):
        pass

    refresh = noop
    noutrefresh = noop
    doupdate = noop

    def get_text_at(self, y, x, len, time=None):
        if time is None:
            global _ticks
            time = _ticks

        e = x + len
        return ''.join([x.at(time) for x in self._screen[y][x:e]])

    def set_input(self, *args):
        printre = re.compile('\w')
        for elm in args:
            if len(elm) == 1 and printre.match(elm):
                self._input_buf.append(ord(elm))
            else:
                self._input_buf.append(elm)

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
    global _scr, _start, _ticks, _print_screen

    if _print_screen:
        print round( 10.0 * (_ticks - _start) ) / 10.0
        print _scr
        print "\n"

def def_prog_mode():
    pass
def endwin():
    global _ticks
    _ticks = 0

_use_delay = True
def use_delay(b):
    global _use_delay
    _use_delay = b

_print_screen = True
def print_screen(b):
    global _print_screen
    _print_screen = b

_scr = None
_start = 0
_ticks = 0


def wrapper(callback):
    global _scr

    if _scr is None:
        _scr = Screen(24,80)
        _scr.set_input('down', 'down', 'q')

    callback(_scr)
