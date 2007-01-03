from core import Drawable, Container, ContainerException
from RowColumns import RowColumns
import curses
import util

class Rows(RowColumns):
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

    def setSize(self, y, x, h, w):
        """
        calculate children's sizes, then call setSize on each of them
        """
        super(Rows, self).setSize(y, x, h, w)

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
            child._meta['height'] = size

            if isinstance(child, Drawable):
                self.log.debug('setting size of "%s" to (%d, %d, %d, %d)', child.name, y, x, child._meta['height'], w)
                child.setSize(y, x, child._meta['height'], w)

            y += child._meta['height']
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
                    self.line(y, borders, self.w - 2 * borders)
                elif child.type == 'blank':
                    self.draw(' ' * (self.w - 2 * borders), y, borders)

            y += child._meta['height']

            # if we're drawing inner borders, do it here
            # but only if there are more rows after this
            if self.innerborder and self.cells.index(child) != len(self.cells) - 1:
                self.line(y, 0, self.w, **attr)
                y += 1 # for ther inner border
