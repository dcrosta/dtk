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

__all__ = ['TextField']

from core import Drawable
from events import TextChanged

class TextField(Drawable):
    """
    A simple one-line textfield that obeys the following keybindings:

    left arrow, right arrow: move cursor one character left or right,
      respectively
    home, end: move cursor to start or end, respectively
    backspace: delete the character just behind the cursor
    delete: delete the character just ahead of the cursor
    
    to have a certain key be the "end" of the input (eg, 'enter' or
    'escape' you must bind it yourself from outside the TextField


    Events (in addition to standard Drawable events):
     * TextChanged
    """

    def __init__(self, **kwargs):
        super(TextField, self).__init__(**kwargs)

        self.buffer = ''
        self.cursor = 0
        self.start = 0

        # keybindings
        self.bindPrintable(self.typing)
        self.bindKey('left', self.moveLeft)
        self.bindKey('right', self.moveRight)
        self.bindKey('home', self.moveToStart)
        self.bindKey('end', self.moveToEnd)
        self.bindKey('backspace', self.backspace)
        self.bindKey('delete', self.delete)

    def setText(self, text):
        self.buffer = text
        self.moveToStart()
        self.touch()

        self.fireEvent(TextChanged(self, self.buffer))

    def getText(self):
        return self.buffer

    def moveLeft(self):
        self.cursor -= 1
        if self.cursor < 0:
            self.cursor = 0

        if self.cursor < self.start:
            self.start = self.cursor

        self.touch()

    def moveRight(self):
        self.cursor += 1
        if self.cursor > len(self.buffer):
            self.cursor = len(self.buffer)

        if self.cursor >= self.start + self.w:
            self.start += 1

        self.touch()

    def moveToStart(self):
        self.cursor = 0

        if self.start > 0:
            self.start = 0

        self.touch()

    def moveToEnd(self):
        self.cursor = len(self.buffer)

        if self.cursor >= self.start + self.w:
            self.start = len(self.buffer) - self.w + 1

        self.touch()

    def backspace(self):
        # the max(0, self.cursor - 1) is necessary to avoid having [:-1] as our slice
        self.buffer = self.buffer[:max(0, self.cursor-1)] + self.buffer[self.cursor:]
        self.moveLeft()

        self.fireEvent(TextChanged(self, self.buffer))

    def delete(self):
        self.buffer = self.buffer[:self.cursor] + self.buffer[self.cursor+1:]

        self.touch()

        self.fireEvent(TextChanged(self, self.buffer))

    def typing(self, _input_key):
        self.buffer = self.buffer[:self.cursor] + _input_key + self.buffer[self.cursor:]
        self.moveRight()

        self.touch()

        self.fireEvent(TextChanged(self, self.buffer))

    def render(self):
        """
        re-displays the buffer into the curses environment
        """

        self.clear()

        self.draw(self.buffer[self.start:], 0, 0)
        if self.focused:
            self.showCursor(0, self.cursor - self.start)
        else:
            self.hideCursor()
