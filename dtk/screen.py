# DTK, a curses "GUI" toolkit for Python programs.
# 
# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# 
# DTK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# DTK is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with Foobar. If not, see <http://www.gnu.org/licenses/>.

import curses
import _curses


class Screen(object):
    """
    Screen handles drawing with attributes for DTK. It does not
    do clipping, so it is suitable for standalone use by programs
    which do not need or want the rest of DTK.

    All drawing methods support keyword arguments for drawing
    attributes (some attributes may not be supported by certain
    terminal types).

    Boolean drawing attribues (mutually exclusive):
    * bold
    * highlight
    * blink
    * dim
    * bright
    * underline

    Color attributes:
    * foreground (or fg)
    * background (or bg)

    Accepted color values:
    * clear
    * white
    * black
    * blue
    * cyan
    * green
    * magenta
    * red
    * yellow
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


    def __init__(self, scr):
        self.scr = scr
        self.auto_update = True

        self.scr.move(0,0)
        self.scr.clrtobot()

    def set_auto_update(self, auto_update):
        self.auto_update = auto_update

    def get_screen_size(self):
        """
        return the size of the screen right now
        """
        h = curses.tigetnum('lines')
        w = curses.tigetnum('cols')
        return h, w

    def draw(self, str, row, col, **kwargs):
        """
        draws the string at the given row and column.
        drawing style is defined by **kwargs.
        """
        h, w = self.scr.getmaxyx()

        # if it's completely off-screen, don't draw
        if row < 0 or row >= h or col >= w:
            return

        # truncate the string to fit
        if col + len(str) > w:
            str = str[:w - col]

        if col < 0:
            str = str[-col:]
            col = 0

        # now draw it
        try:
            self.scr.addstr(row, col, str, self._drawing_attr(kwargs))
        except _curses.error:
            pass

        if self.auto_update:
            self.scr.refresh()

    def draw_down(self, str, row, col, **kwargs):
        """
        draws the string at the position given by row and col, with
        the drawing style defined by arguments given in **kwargs.
        these will often include things like face attributes (bold,
        underline, etc), colors, and other things specific to the
        Engine. capabilities() should list all the possibilities.
        """
        h, w = self.scr.getmaxyx()

        if row > h or col < 0 or col > w:
            return

        attr = self._drawing_attr(kwargs)

        for char, r in zip(str, range(row, min(row + len(str), h))):
            try:
                self.scr.addstr(r, col, char, attr)
            except _curses.error:
                pass

        if self.auto_update:
            self.scr.refresh()

    def box(self, row, col, box_width, box_height, **kwargs):
        """
        draws a line using border characters, starting at the location
        (row, col) with the given width and height. fails silently if
        any part of the box is outside the Drawable's bounds
        """
        h, w = self.get_screen_size()

        # check bounds
        if col < 0 or row < 0 or col + box_width > w or row + box_height > h:
            return

        attr = self._drawing_attr(kwargs)

        # draw corners
        self.scr.addch(row, col, curses.ACS_ULCORNER, attr)
        self.scr.addch(row, col + box_width - 1, curses.ACS_URCORNER, attr)
        self.scr.addch(row + box_height - 1, col, curses.ACS_LLCORNER, attr)
        try:
            self.scr.addch(row + box_height - 1, col + box_width - 1, curses.ACS_LRCORNER, attr)
        except _curses.error, e:
            pass

        # draw edges
        if attr:
            # if we have an attribute, we have to draw char-brow-char
            for r in range(col + 1, col + box_width - 1):
                self.scr.addch(row, r, curses.ACS_HLINE, attr)
                self.scr.addch(row + box_height - 1, r, curses.ACS_HLINE, attr)
    
            for c in range(row + 1, row + box_height - 1):
                self.scr.addch(c, col, curses.ACS_VLINE, attr)
                self.scr.addch(c, col + box_width - 1, curses.ACS_VLINE, attr)

        else:
            # else we can use these functions which are probably quicker
            self.scr.hline(row, col + 1, curses.ACS_HLINE, box_width - 2)
            self.scr.hline(row + box_height - 1, col + 1, curses.ACS_HLINE, box_width - 2)

            self.scr.vline(row + 1, col, curses.ACS_VLINE, box_height - 2)
            self.scr.vline(row + 1, col + box_width - 1, curses.ACS_VLINE, box_height - 2)

        if self.auto_update:
            self.scr.refresh()

    def line(self, row, col, len, **kwargs):
        """
        """
        h, w = self.get_screen_size()

        # invisible line
        if row < 0 or row > h:
            return

        if col < 0:
            len += col
            col = 0
        if col + len > w:
            len -= (w - len)

        attr = self._drawing_attr(kwargs)

        if 'leftEnd' in kwargs:
            self.scr.addch(row, col, kwargs['leftEnd'], attr)
            len -= 1
            col += 1

        if 'rightEnd' in kwargs:
            self.scr.addch(row, col + len - 1, kwargs['rightEnd'], attr)
            len -= 1

        if attr:
            for c in range(col, col + len):
                self.scr.addch(row, c, curses.ACS_HLINE, attr)
        else:
            self.scr.hline(row, col, curses.ACS_HLINE, len)

        if self.auto_update:
            self.scr.refresh()

    def line_down(self, row, col, len, **kwargs):
        """
        """
        h, w = self.get_screen_size()

        # invisible line
        if col < 0 or col > w:
            return

        if row < 0:
            len += row
            row = 0
        if row + len > h:
            len -= (h - len)

        attr = self._drawing_attr(kwargs)

        if 'topEnd' in kwargs:
            self.scr.addch(row, col, kwargs['topEnd'], attr)
            len -= 1
            row += 1

        if 'bottomEnd' in kwargs:
            self.scr.addch(row + len - 1, col, kwargs['bottomEnd'], attr)
            len -= 1

        if attr:
            for r in range(row, row + len):
                self.scr.addch(r, col, curses.ACS_VLINE, attr)
        else:
            self.scr.vline(row, col, curses.ACS_VLINE, len)

        if self.auto_update:
            self.scr.refresh()

    def clear(self):
        """
        clears the whole screen
        """
        self.scr.move(0, 0)
        self.scr.clrtobot()

        if self.auto_update:
            self.scr.refresh()

    def clear_range(self, y, x, h, w):
        """
        clears a range
        """
        for y in range(y, y+h):
            for x in range(x, x+w):
                try:
                    self.scr.delch(y, x)
                    self.scr.insch(y, x, ' ')
                except:
                    pass

        if self.auto_update:
            self.scr.refresh()

    def _drawing_attr(self, attrdict):
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

        attr |= self._lookup_color_pair(fg, bg)

        return attr

    def _lookup_color_pair(self, fg, bg):
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

