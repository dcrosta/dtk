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

__all__ = ['Row', 'RowLayout']

from core import Drawable, Container, ContainerException
from RowColumns import RowColumns
import curses
import util

class Row(object):

    def __init__(self, drawable, height=None):
        self.drawable = drawable
        self.height = height

class RowLayout(RowColumns):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the row, or both.
    """

    addRow = RowColumns.addChild
    insertRow = RowColumns.insertChild
    nextRow = RowColumns.nextChild
    prevRow = RowColumns.prevChild
    switchRow = RowColumns.switchChild
    lineSomehow = RowColumns.line
    drawSomehow = RowColumns.draw

    def __init__(self, *args, **kwargs):
        RowColumns.__init__(self, **kwargs)

        # expect *args to be a list of Drawables,
        # or possibly adapted Drawables

        for arg in args:
            if isinstance(arg, Row):
                self.addRow(arg.drawable, fixedsize=arg.height)
            else:
                self.addRow(arg)

    def setSize(self, y, x, h, w):
        """
        calculate children's sizes, then call setSize on each of them
        """
        super(RowLayout, self).setSize(y, x, h, w)

        # this is the case when we're being resized before
        # the Engine is initialized
        if y == 0 and x == 0 and h == 0 and w == 0:
            return

        self.log.debug('setSize(%d, %d, %d, %d)' % (y, x, h, w))

        # use the values from parent's setSize()
        y = self.y
        x = self.x
        h = self.h
        w = self.w

        # start from available height
        available = h

        # adjust for borders, if they're to be drawn
        if self.outerborder:
            available -= 2

            # pushes the starting y down by 1
            y += 1
            
            # outer border will also shrink our available horizontal area
            x += 1
            w -= 2

        if self.innerborder:
            available -= (len(self.cells) - 1)


        items = [(item._meta['fixedsize'], item._meta['weight']) for item in self.cells]

        sizes = util.flexSize(items, available)

        for (child, size) in zip(self.cells, sizes):
            child._meta['primary_dim'] = size

            if isinstance(child, Drawable):
                self.log.debug('setting size of "%s" to (%d, %d, %d, %d)', child.name, y, x, child._meta['primary_dim'], w)
                child.setSize(y, x, child._meta['primary_dim'], w)

            y += child._meta['primary_dim']
            if self.innerborder:
                y += 1

    def render(self):
        """
        draw the borders
        """
        attr = {}
        if self.outerborder:
            self.box(0, 0, self.w, self.h)
            attr['leftEnd'] = curses.ACS_LTEE
            attr['rightEnd'] = curses.ACS_RTEE

        # 1 if true, 0 if false
        borders = int(self.outerborder) 

        y = borders

        for child in self.cells:
            if isinstance(child, self.Separator):
                if child.type == 'line':
                    self.lineSomehow(y, borders, self.w - 2 * borders)
                elif child.type == 'blank':
                    self.drawSomehow(' ' * (self.w - 2 * borders), y, borders)

            y += child._meta['primary_dim']

            # if we're drawing inner borders, do it here
            # but only if there are more rows after this
            if self.innerborder and self.cells.index(child) != len(self.cells) - 1:
                self.lineSomehow(y, 0, self.w, **attr)
                y += 1 # for ther inner border
