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


from core import Drawable
import util

import types
import re



class TextEditor(Drawable):
    """
    A simple multi-line text edtor/viewer that does smart things.

    Events:
     * 'text changed' whenever the text changes
    """

    def __init__(self, editable = True, **kwargs):
        super(TextEditor, self).__init__(**kwargs)

        # the buffer of lines
        self.buffer = ['']
        self.cy = 0
        self.cx = 0

        # key bindings
        self.editable = editable
        if self.editable:
            self.bindPrintable(self.typing)
            self.bindKey('enter', self.typing)
            self.bindKey('backspace', self.backspace)
            self.bindKey('delete', self.delete)

        self.bindKey('up',        self.moveUp)
        self.bindKey('down',      self.moveDown)
        self.bindKey('left',      self.moveLeft)
        self.bindKey('right',     self.moveRight)
        self.bindKey('home',      self.moveToHome)
        self.bindKey('end',       self.moveToEnd)
        self.bindKey('page up',   self.pageUp)
        self.bindKey('page down', self.pageDown)


    def typing(self, _input_key):
        """
        handles printable input and updates the cursor position
        for normal typing
        """
        input = _input_key
        input = _input_key
        # if the input is 'enter', then insert a new line into the 
        # buffer and move the cursor to it
        if input == 'enter':
            self.cy += 1
            self.cx = 0
            self.buffer.insert(self.cy, '')

            self.touch()
            return

        line = self.buffer[self.cy]
        self.buffer[self.cy] = line[:self.cx] + input + line[self.cx:]

        self.cx += 1

        self.touch()

        self.fireEvent('text changed')


    def backspace(self):
        """
        called when the user hits the backspace key
        """

        if self.cx == 0 and self.cy > 0:
            # if we're at the beginning of a line
            self.cx = len(self.buffer[self.cy - 1])
            self.buffer[self.cy - 1] = self.buffer[self.cy - 1] + self.buffer[self.cy]
            del self.buffer[self.cy]
            self.cy -= 1
        
        elif self.cx > 0:
            # else just delete the char before us
            line = self.buffer[self.cy]
            self.buffer[self.cy] = line[:self.cx - 1] + line[self.cx:]
            self.cx -= 1

        self.touch()

        self.fireEvent('text changed')
    

    def delete(self):
        if self.cx == len(self.buffer[self.cy]) and self.cy < len(self.buffer) - 1:
            # if we hit delete at the end of a line
            self.buffer[self.cy] += self.buffer[self.cy + 1]
            del self.buffer[self.cy + 1]

        else:
            line = self.buffer[self.cy]
            self.buffer[self.cy] = line[:self.cx] + line[self.cx + 1:]

        self.touch()

        self.fireEvent('text changed')


    def moveHome(self):
        """
        move the cursor to the start of the buffer.
        distinct from moveToHome
        """
        self.cx, self.cy = (0,0)
        self.touch()


    def moveToHome(self):
        self.cx = 0
        self.touch()


    def moveToEnd(self):
        self.cx = len(self.buffer[self.cy])
        self.touch()
        

    def pageUp(self):
        """
        this behavior is modelled on the text editor widget in trac.
        this is different from emacs' behavior, but i think this
        is the more common behavior.
        """
        self.cy -= self.h
        if self.cy < 0:
            self.cy = 0
            self.cx = 0
        elif self.cx > len(self.buffer[self.cy]):
            self.cx = len(self.buffer[self.cy])
        self.touch()


    def pageDown(self):
        """
        this behavior is modelled on the text editor widget in trac.
        this is different from emacs' behavior, but i think this
        is the more common behavior.
        """
        self.cy += self.h
        if self.cy >= len(self.buffer):
            self.cy = len(self.buffer) - 1
            self.cx = len(self.buffer[self.cy])
        elif self.cx > len(self.buffer[self.cy]):
            self.cx = len(self.buffer[self.cy])
        self.touch()

    
    def moveLeft(self):
        if self.cx == 0 and self.cy > 0:
            self.cy -= 1
            self.cx = len(self.buffer[self.cy])

        elif self.cx > 0:
            self.cx -= 1

        self.touch()


    def moveRight(self):
        if self.cx == len(self.buffer[self.cy]) and self.cy < len(self.buffer) - 1:
            self.cx = 0
            self.cy += 1

        elif self.cx < len(self.buffer[self.cy]):
            self.cx += 1

        self.touch()


    def moveDown(self):
        if self.cy < len(self.buffer) - 1:
            self.cy += 1

            if len(self.buffer[self.cy]) < self.cx:
                self.cx = len(self.buffer[self.cy])

        self.touch()


    def moveUp(self):
        if self.cy > 0:
            self.cy -= 1

            if len(self.buffer[self.cy]) < self.cx:
                self.cx = len(self.buffer[self.cy])
        
        self.touch()
        
    
    def setText(self, text):
        """
        accepts a list of strings (each string is a paragraph in the
        editor) or a single string, which is split by newline
        characters ('\n').
        """
        if type(text) in types.StringTypes:
            self.buffer = text.split('\n')
        elif type(text) in [types.ListType, types.TupleType]:
            self.buffer = list(text)

        self.touch()

        self.fireEvent('text changed')


    def getText(self):
        """
        returns the list of strings currently in the TextEditor's
        buffer
        """
        return self.buffer


    def render(self):
        wrapped = []
        for line in self.buffer:
            wrapped.extend(util.wrap(line, self.w))


        self.clear()

        y = 0
        for line in wrapped:
            self.draw(line, y, 0)
            y += 1

        # TODO
        # have to have a more intelligent calculation (taking into
        # account line wrapping) of where the cursor is... that might
        # take some work, or really we'll just need to move the wrapping
        # into this class
        if self.focused:
            if self.editable and self.cx == self.w:
                self.showCursor(self.cy + 1, 0)
            elif self.editable:
                self.showCursor(self.cy, self.cx)
            else:
                self.hideCursor()
        else:
            self.hideCursor()
