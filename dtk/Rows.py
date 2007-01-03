from core import Drawable, Container, ContainerException

import curses
import util

class Rows(Container):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the row, or both.
    """

    class Separator:
        def __init__(self, type):
            self.fixedsize = 1
            self.height = 1 
            self.weight = 0
            self.type = type


    def __init__(self, outerborder = True, innerborder = True, **kwargs):
        super(Rows, self).__init__(**kwargs)

        self.outerborder = outerborder
        self.innerborder = innerborder
        self.rows = []

        self.bindKey('tab', self.nextRow)

    def addRow(self, drawable, fixedsize = None, weight = 1):
        """
        add a row (will become the bottom row) containing
        the given drawable (its parent should be this RowLayout),
        which will be drawn with the appropriate minimum and
        maximum height, as space allows. weight is used to calculate
        how to distribute remaining space after minimum and maximum
        are taken into account.
        """
        drawable._meta = dict(fixedsize=fixedsize, weight=weight)
        if not len(self.children):
            self.active = drawable
        self.children.append(drawable)
        self.rows.append(drawable)
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
        self.rows.append(sep)
        self.touch()

    def insertRow(self, drawable, fixedsize = None, weight = 1):
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
        if not len(self.children):
            self.active = drawable
        self.children.insert(index, drawable)
        self.rows.insert(index, drawable)
        self.touch()


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
            available -= (len(self.rows) - 1)


        items = [(item._meta['fixedsize'], item._meta['weight']) for item in self.rows]

        sizes = util.flexSize(items, available)

        for (child, size) in zip(self.rows, sizes):
            child._meta['height'] = size

            if isinstance(child, Drawable):
                self.log.debug('setting size of "%s" to (%d, %d, %d, %d)', child.name, y, x, child._meta['height'], w)
                child.setSize(y, x, child._meta['height'], w)

            y += child._meta['height']
            if self.innerborder:
                y += 1


    def drawContents(self):
        """
        call drawContents() on each of our children
        """
        for child in self.children:
            if isinstance(child, Drawable):
                child.drawContents()

        # draw borders through render()
        #super(Rows, self).drawContents()
        # this is not ideal, but Container.drawContents throws an exception, so.
        Drawable.drawContents(self)

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

        for child in self.rows:
            if isinstance(child, self.Separator):
                if child.type == 'line':
                    self.line(y, borders, self.w - 2 * borders)
                elif child.type == 'blank':
                    self.draw(' ' * (self.w - 2 * borders), y, borders)

            y += child._meta['height']

            # if we're drawing inner borders, do it here
            # but only if there are more rows after this
            if self.innerborder and self.rows.index(child) != len(self.rows) - 1:
                self.line(y, 0, self.w, **attr)
                y += 1 # for ther inner border


    def nextRow(self):
        index = self.children.index(self.active) + 1
        if index >= len(self.children):
            index = 0
        self.switchRow(index)


    def prevRow(self):
        index = self.children.index(self.active) - 1
        if index == 0:
            index += len(self.children)
        self.switchRow(index)
        

    def switchRow(self, index):
        self.log.debug('switching row from %s to %s' % (self.children.index(self.active), index))
        self.active.touch()
        self.active = self.children[index]
        self.touch()
        self.active.touch()
