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

__all__ = ['Slideshow']

from core import Container, ContainerException
import curses
import util

class Slideshow(Container):
    """
    implements a simple layout scheme for Drawables which
    holds an arbitrary number of Drawables and only displays
    one at a time.

    Events:
     * 'active child changed' when a new slide is shown
    """

    def __init__(self, *args, **kwargs):
        super(Slideshow, self).__init__(*args, **kwargs)
        self.bindKey('tab', self.nextSlide)
    
    def addSlide(self, drawable):
        """
        add a Drawable to the end of the list of slides. the
        newly-added Drawable will be hidden by default unless
        it is the only slide in the slideshow.
        """                
        self.children.append(drawable)
        if self.active:
            drawable.setSize(0, 0, 0, 0)
        else:
            self.setActiveDrawable(drawable)

    def _setChildSizes(self):
        """
        hide all child Drawables except the currently-viewed one.
        """
        y, x, h, w = self.y, self.x, self.h, self.w

        for child in self.children:
            if child == self.active:
                child.setSize(y, x, h, w)
            else:
                child.setSize(0, 0, 0, 0)

    def setSize(self, y, x, h, w):
        super(Slideshow, self).setSize(y, x, h, w)

        self.log.debug('setSize(%d, %d, %d, %d)' % (y, x, h, w))
        self._setChildSizes()
        
    def nextSlide(self):
        index = self.children.index(self.active) + 1
        if( index >= len(self.children) ):
            index = 0
        self.setActiveDrawable(self.children[index])
        self._setChildSizes()

    def previousSlide(self):
        index = self.children.index(self.active) - 1
        if( index < 0 ):
            index = len(self.children) - 1
        self.setActiveDrawable(self.children[index])
        self._setChildSizes()

    def showSlide(self, slide):
        if slide not in self.children:
            return False
        self.setActiveDrawable(slide)
        self._setChildSizes()

    def drawContents(self):
        self.active.drawContents()
