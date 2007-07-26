# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# All rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share to copy, distribute, display, and perform the work
#   * to Remix to make derivative works
# 
# Under the following conditions:
# 
#   * Attribution. You must attribute the work in the manner specified by the
#     author or licensor (but not in any way that suggests that they endorse you
#     or your use of the work).
#   * Share Alike. If you alter, transform, or build upon this work, you may
#     distribute the resulting work only under the same, similar or a compatible
#     license.
# 
#   * For any reuse or distribution, you must make clear to others the license
#     terms of this work.
#   * Any of the above conditions can be waived if you get permission from the
#     copyright holder.
#   * Apart from the remix rights granted under this license, nothing in this
#     license impairs or restricts the author's moral rights.
# 
# 
# Full text of the license can be found online:
# 
#   <http://creativecommons.org/licenses/by-sa/3.0/us/>


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

    class Separator:
        def __init__(self, type):
            self.fixedsize = 1
            self.thickness = 1 
            self.weight = 0
            self.type = type

    def __init__(self, outerborder = True, innerborder = True, **kwargs):
        if not issubclass(self.__class__, RowColumns):
            raise ContainerException("do not create a RowColumns instance. instantiate a subclass of RowColumns instead.")

        super(RowColumns, self).__init__(**kwargs)

        self.outerborder = outerborder
        self.innerborder = innerborder
        self.cells = []

        self.bindKey('tab', self.nextChild)

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
