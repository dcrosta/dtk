from Drawable import Drawable
import util

import types
import re



class TextEditor(Drawable):
    """
    A simple multi-line text edtor/viewer that does smart things.
    """

    def __init__(self, parent, name, editable = True):
        super(TextEditor, self).__init__(parent, name)

        # the buffer of lines
        self.buffer = ['']
        self.cy = 0
        self.cx = 0

        # key bindings
        if editable:
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


    def dopass(self):
        pass

    # temporary -- do nothing for all these funcs
    moveToHome = moveToEnd = pageUp = pageDown = dopass


    def typing(self, input):
        """
        handles printable input and updates the cursor position
        for normal typing
        """

        # if the input is 'enter', then insert a new line into the 
        # buffer and move the cursor to it
        if input == 'enter':
            self.cy += 1
            self.cx = 0
            self.log('adding new line %d' % self.cy)
            self.buffer.insert(self.cy, '')

            self.touch()
            return

        line = self.buffer[self.cy]
        self.buffer[self.cy] = line[:self.cx] + input + line[self.cx:]

        self.cx += 1

        self.touch()


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
    

    def delete(self):
        if self.cx == len(self.buffer[self.cy]) and self.cy < len(self.buffer) - 1:
            # if we hit delete at the end of a line
            self.buffer[self.cy] += self.buffer[self.cy + 1]
            del self.buffer[self.cy + 1]

        else:
            line = self.buffer[self.cy]
            self.buffer[self.cy] = line[:self.cx] + line[self.cx + 1:]

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

        self.log('wrapped: %s' % wrapped)

        self.clear()
        self.log('cursor: %d, %d' % (self.cy, self.cx))

        y = 0
        for line in wrapped:
            self.draw(line, y, 0)
            y += 1

        # have to have a more intelligent calculation (taking into
        # account line wrapping) of where the cursor is... that might
        # take some work, or really we'll just need to move the wrapping
        # into this class
        if self.cx == self.w:
            self.showCursor(self.cy + 1, 0)
        else:
            self.showCursor(self.cy, self.cx)
