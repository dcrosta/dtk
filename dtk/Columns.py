# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# Some rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share -- to copy, distribute, display, and perform the work
#   * to Remix -- to make derivative works
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
from RowColumns import RowColumns
import curses
import util

class Columns(RowColumns):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the columns, or both.
    """

    addColumn = RowColumns.addChild
    insertColumn = RowColumns.insertChild
    nextColumn = RowColumns.nextChild
    prevColumn = RowColumns.prevChild
    switchColumn = RowColumns.switchChild
    lineSomehow = RowColumns.lineDown
    drawSomehow = RowColumns.drawDown

    def setSize(self, y, x, h, w):
        """
        calculate children's sizes, then call setSize on each of them
        """
        super(Columns, self).setSize(y, x, h, w)

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

        # start from available width
        available = w

        # adjust for borders, if they're to be drawn
        if self.outerborder:
            available -= 2

            # pushes the starting x over by 1
            x += 1
            
            # outer border will also shrink our available vertical area
            y += 1
            h -= 2

        if self.innerborder:
            available -= (len(self.cells) - 1)


        items = [(item._meta['fixedsize'], item._meta['weight']) for item in self.cells]

        sizes = util.flexSize(items, available)

        for (child, size) in zip(self.cells, sizes):
            child._meta['primary_dim'] = size

            if isinstance(child, Drawable):
                self.log.debug('setting size of "%s" to (%d, %d, %d, %d)', child.name, y, x, h, child._meta['primary_dim'])
                child.setSize(y, x, h, child._meta['primary_dim'])

            x += child._meta['primary_dim']
            if self.innerborder:
                x += 1
        
    def render(self):
        """
        draw the borders
        """
        attr = {}
        if self.outerborder:
            self.box(0, 0, self.w, self.h)
            attr['topEnd'] = curses.ACS_TTEE
            attr['bottomEnd'] = curses.ACS_BTEE

        # 1 if true, 0 if false
        borders = int(self.outerborder)

        x = borders 

        for child in self.cells:
            if isinstance(child, self.Separator):
                if child.type == 'line':
                    self.lineSomehow(borders, x, self.h - 2 * borders)
                elif child.type == 'blank':
                    self.drawSomehow(' ' * (self.h - 2 * borders), 0, x + borders)

            x += child._meta['primary_dim']

            # if we're drawing inner borders, do it here
            # but only if there are more cols after this
            if self.innerborder and self.cells.index(child) != len(self.cells) - 1:
                self.lineSomehow(0, x, self.h, **attr)
                x += 1 # for the inner border
