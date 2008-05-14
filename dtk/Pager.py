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

__all__ = ['Pager']

import types

import util
from core import Drawable

class Pager(Drawable):
    """
    A simple drawable that displays a scrollable, optionally
    line-wrapped piece of text, similar to the less program.
    No editing features are provided.
    """


    def __init__(self, vimlike = False, **kwargs):
        """
        Pager takes an optional parameter 'vimlike': when
        True enables bindings for vim-like navigation (j/k
        for up/down)
        """
        super(Pager, self).__init__(**kwargs)

        self.firstVisible = 0

        self.text = ''
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
        self.firstVisible = 0
        self.lines = None
        self.text = str(text)
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
        redraw what's in the visible range, based on our
        size and firstVisible
        """

        if self.lines is None:
            self.lines = util.wrap(self.text, self.w)

        self.clear()

        for i in range(self.firstVisible, min(len(self.lines), self.firstVisible + self.h)):
            self.draw(self.lines[i], i - self.firstVisible, 0);
