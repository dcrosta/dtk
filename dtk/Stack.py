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

__all__ = ['Stack']

from core import Drawable, Container, ContainerException

class Stack(Container):
    """
    Basic stack of drawables.
    """

    def __init__(self, **kwargs):
        super(Stack, self).__init__(**kwargs)


    def __len__(self):
        """
        return the number of items currently on the stack
        """
        return len(self.children)


    def push(self, drawable):
        """
        push a new element onto the stack. If the previous
        top Drawable was focused, then the new drawable will
        be set active automatically. if `drawable` already exists
        in the Stack, it will be removed first, then placed on
        top.
        """        
        # make sure there's only one copy of it
        # on the stack at any time
        if drawable in self.children:
            self.children.remove(drawable)

        self.children.append(drawable)

        drawable.setSize(self.y, self.x, self.h, self.w)
        self.setActiveDrawable(drawable)

        self.touch()


    def pop(self):
        """
        pop and return the top element off the stack. if the
        previous top stack Drawable was focused, the element
        underneath (if any) will be focused automatically. if
        the stack is empty after popping this element and that
        element had focus, then the stack itself is given
        focus
        """
        drawable = None

        if len(self.children):
            drawable = self.children.pop()

            if self.active is drawable:
                if len(self.children):
                    self.setActiveDrawable(self.children[-1])
                else:
                    self.log.debug('forcing focus on self')
                    self.engine.setFocus(self)

        if len(self.children):
            self.children[-1].setSize(self.y, self.x, self.h, self.w)

        self.clear()
        self.touch()

        return drawable


    def setSize(self, y, x, h, w):
        super(Stack, self).setSize(y, x, h, w)

        if len(self.children):
            self.children[-1].setSize(self.y, self.x, self.h, self.w)

        self.touch()


    def drawContents(self):
        if len(self.children):
            self.children[-1].drawContents()
