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

__all__ = []

from core import Drawable, Container, ContainerException

import curses
import util

class RowColumns(Container):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the row, or both.
    """

    # these things are all set by the implementing
    # class, either RowLayout or ColumnLayout
    addRow = None
    insertRow = None
    nextRow = None
    prevRow = None
    switchRow = None
    lineSomehow = None
    drawSomehow = None
    adapterClass = None

    class Separator:
        def __init__(self, type):
            self.fixedsize = 1
            self.thickness = 1 
            self.weight = 0
            self.type = type

    def __init__(self, *args, **kwargs):
        if not issubclass(self.__class__, RowColumns):
            raise ContainerException("do not create a RowColumns instance. instantiate a subclass of RowColumns instead.")

        super(RowColumns, self).__init__(**kwargs)

        self.outerborder = kwargs.get('outerborder', True)
        self.innerborder = kwargs.get('innerborder', True)
        self.cells = []

        self.bindKey('tab', self.nextChild)

        # expect args to be a list of Drawables,
        # or possibly adapted Drawables
        did_set_focus = False
        for i, arg in enumerate(args):
            if isinstance(arg, self.adapterClass):
                self.addChild(arg.drawable, fixedsize=arg.fixedsize)
                if arg.focused:
                    if did_set_focus:
                        raise ContainerException("only one child may have focus")
                    self.switchChild(i)
                    did_set_focus = True
            else:
                self.addChild(arg)

    def addChild(self, drawable, fixedsize = None, weight = 1):
        """
        add a row (will become the bottom row) containing
        the given drawable (its parent should be this RowLayout),
        which will be drawn with the appropriate minimum and
        maximum height, as space allows. weight is used to calculate
        how to distribute remaining space after minimum and maximum
        are taken into account.
        """
        first_child = len(self.children) == 0

        drawable._meta = dict(fixedsize=fixedsize, weight=weight)
        self.children.append(drawable)
        if first_child:
            self.setActiveDrawable(drawable)
        self.cells.append(drawable)
        self.touch()

    def addSeparator(self, type = 'line'):
        """
        adds a 'separator row', which contains a horizontal line
        akin to those drawn when internal borders are enabled.

        @param type: 'line' draws a horizontal line like the borders;
            'blank' leaves a blank row 1 character high
        @type  type: string
        """
        sep = self.Separator(type)
        sep._meta = dict(fixedsize=1, weight=None)
        self.cells.append(sep)
        self.touch()

    def insertChild(self, drawable, fixedsize = None, weight = 1):
        """
        same mechanics as addRow, but it inserts it in the indexth
        position in the row list. if index > num rows, it will
        be the bottom; if index <= 0, it will be the top
        row. the indices are not stored, so:

        rows.addRow(foo, ...)
        rows.insertRow(bar, 10, ...)
        rows.insertRow(baz, 5, ...)

        will result in the row ordered foo, bar, baz from top-
        to-bottom. (that is, the insertion works as it would on any
        ordinary python list)

        weight is used to calculate how to distribute remaining space
        after minimum and maximum are taken into account.
        """
        drawable._meta = dict(fixedsize=fixedsize, weight=weight)
        first_child = len(self.children) == 0
        self.children.insert(index, drawable)
        if first_child:
            self.setActiveDrawable(drawable)
        self.cells.insert(index, drawable)
        self.touch()

    def setSize(self, y, x, h, w):
        if not issubclass(self.__class__, RowColumns):
            raise ContainerException("setSize method not implemented")
        else:
            super(RowColumns, self).setSize(y, x, h, w)

    def render(self):
        if not issubclass(self.__class__, RowColumns):
            raise ContainerException("render method not implemented")
        else:
            super(RowColumns, self).render()

    def drawSomehow(self, *args, **kwargs):
        raise ContainerException("no draw method specified.")

    def lineSomehow(self, *args, **kwargs):
        raise ContainerException("no line method specified.")

    def drawContents(self):
        """
        call drawContents() on each of our children
        """
        for child in self.children:
            child.drawContents()

        # draw borders through render()
        super(RowColumns, self).drawContents()

    def nextChild(self):
        index = self.children.index(self.active) + 1
        if index >= len(self.children):
            index = 0
        self.switchChild(index)

    def prevChild(self):
        index =self.children.index(self.active) - 1
        if index == 0:
            index += len(self.children)
        self.switchChild(index)

    def switchChild(self, index):
        """
        switches internal focus to the given child index
        if the given index is in range.
        """
        self.setActiveDrawable(self.children[index])
        self.touch()
