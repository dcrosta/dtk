import types

import util
from Drawable import Drawable

class Pager(Drawable):


    def __init__(self, parent, name, vimlike = False):
        super(Pager, self).__init__(parent, name)

        self.firstVisible = 0

        self.text = None
        self.lines = None

        self.bindKey('down', self.moveDown)
        self.bindKey('up', self.moveUp)
        self.bindKey('page down', self.pageDown)
        self.bindKey('page up', self.pageUp)
        self.bindKey('home', self.moveToTop)
        self.bindKey('end', self.moveToBottom)

        if vimlike:
            self.bindKey('j', self.moveDown)
            self.bindKey('k', self.moveUp)

    
    def setText(self, text):
        """
        set the pager text to the given text.

        @param text: the text to use, as a
            newline formatted string
        @type  text: string
        """
        self.lines = None
        self.text = text
        self.touch()

    
    def getText(self):
        """
        return the text as given us

        @return: the text in the pager
        @rtype:  string
        """
        return self.text


    def moveToTop(self):
        """
        move the highlight to the first item
        """
        self.firstVisible = 0
        self.touch()


    def moveToBottom(self):
        """
        move the highlight to the last item
        """
        self.firstVisible = max(0, len(self.lines) - self.h)
        self.touch()


    def moveUp(self):
        """
        move the highlight up one item
        """
        self.firstVisible -= 1
        if self.firstVisible < 0:
            self.firstVisible = 0
        self.touch()


    def moveDown(self):
        """
        move the highlight down one item
        """
        self.firstVisible += 1
        if self.firstVisible > len(self.lines) - 1:
            self.firstVisible = len(self.lines) - 1
        self.touch()


    def pageDown(self):
        """
        move down by self.height rows
        """
        self.firstVisible += self.h
        if self.firstVisible > len(self.lines) - 1:
            self.firstVisible = len(self.lines) - 1
        self.touch()


    def pageUp(self):
        """
        move up by self.height rows
        """
        self.firstVisible -= self.h
        if self.firstVisible < 0:
            self.firstVisible = 0
        self.touch()


    def setSize(self, y, x, h, w):
        self.lines = None
        super(Pager, self).setSize(y, x, h, w)
        self.touch()


    def render(self):
        """
        if this gets called, then one of our functions has indicated
        that it's time for a redraw (through self.touch()), so we're
        going to re-draw what's in the visible range, based on our
        size and what is currently firstVisible
        """

        if self.lines is None:
            self.lines = util.wrap(self.text, self.w)

        self.clear()

        for i in range(self.firstVisible, min(len(self.lines), self.firstVisible + self.h)):
            line = str(self.lines[i])
            if len(line) > self.w:
                line = line[:self.w]

            # pad the line with spaces
            if len(line) < self.w:
                line += ' ' * (self.w - len(line))

            self.draw(line, i - self.firstVisible, 0);
