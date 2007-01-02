from core import Drawable, Container, ContainerException
import curses
import util

class Columns(Container):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the columns, or both.
    """

#    class Column:
#        def __init__(self, drawable, fixedsize, weight):
#            self.drawable = drawable
#            self.fixedsize = fixedsize
#            self.weight = weight
#            self.width = None 

    class Separator:
        def __init__(self, type):
            self.fixedsize = 1
            self.width = 1 
            self.weight = 0
            self.type = type


    def __init__(self, outerborder = True, innerborder = True, **kwargs):
        super(Columns, self).__init__(**kwargs)

        # save these for later use
        self.outerborder = outerborder
        self.innerborder = innerborder
        self.columns = []

        self.bindKey('tab', self.nextColumn)

    def addColumn(self, drawable, fixedsize = None, weight = 1):
        """
        add a column (will become the rightmost column) containing
        the given drawable (its parent should be this ColumnLayout),
        which will be drawn with the appropriate minimum and
        maximum width, as space allows. weight is used to calculate
        how to distribute remaining space after minimum and maximum
        are taken into account.
        """
        drawable._meta = dict(fixedsize=fixedsize, weight=weight)
        if not len(self.children):
            self.active = drawable
        self.children.append(drawable)
        self.columns.append(drawable)
        self.touch()

    def addSeparator(self, type = 'line'):
        """
        adds a 'separator row', which contains a horizontal line
        akin to those drawn when internal borders are enabled.

        @param type: 'line' draws a vertical line like the borders;
            'blank' leaves a blank column 1 character wide
        @type  type: string
        """
        sep = self.Separator(type)
        sep._meta = dict(fixedsize=1, weight=None)
        self.separators.append(sep)
        self.touch()

    def insertColumn(self, drawable, fixedsize = None, weight = 1):
        """
        same mechanics as addColumn, but it inserts it in the indexth
        position in the column list. if index > num columns, it will
        be the rightmost column; if index < 0, it will be the leftmost
        column. the indices are not stored, so:

        cols.addColumn(foo, ...)
        cols.insertColumn(bar, 10, ...)
        cols.insertColumn(baz, 5, ...)

        will result in the columns ordered foo, bar, baz from left-
        to-right. (that is, the insertion works as it would on any
        ordinary python list)

        weight is used to calculate how to distribute remaining space
        after minimum and maximum are taken into account.
        """
        drawable._meta = dict(fixedsize=fixedsize, weight=weight)
        if not len(self.children):
            self.active = drawable
        self.children.insert(index, drawable)
        self.touch()

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
            available -= (len(self.columns) - 1)


        items = [(item._meta['fixedsize'], item._meta['weight']) for item in self.columns]

        sizes = util.flexSize(items, available)

        for (child, size) in zip(self.columns, sizes):
            child._meta['width'] = size

            if isinstance(child, Drawable):
                self.log.debug('setting size of "%s" to (%d, %d, %d, %d)', child.name, y, x, h, child._meta['width'])
                child.setSize(y, x, h, child._meta['width'])

            x += child._meta['width']
            if self.innerborder:
                x += 1
        

    def drawContents(self):
        """
        call drawContents() on each of our children
        """
        for child in self.children:
            child.drawContents()

        # draw borders through render()
        #super(Columns, self).drawContents()
        # this is not ideal, but Container.drawContents throws an exception, so.
        Drawable.drawContents(self)


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

        for child in self.columns:
            if isinstance(child, self.Separator):
                if child.type == 'line':
                    self.lineDown(0, x, self.h)
                elif child.type == 'blank':
                    self.drawDown(' ' * (self.h - 2 * borders), 0, x)

            x += child._meta['width']

            # if we're drawing inner borders, do it here
            # but only if there are more cols after this
            if self.innerborder and self.columns.index(child) != len(self.columns) - 1:
                self.lineDown(0, x, self.h, **attr)
                x += 1 # for the inner border


    def nextColumn(self):
        index = self.children.index(self.active) + 1
        if index >= len(self.children):
            index = 0
        self.switchColumn(index)


    def prevColumn(self):
        self.switchColumn(self.children.index(self.active) - 1)


    def switchColumn(self, index):
        """
        switches internal focus to the given column index, if it's
        in range. otherwise, switches the focused column one to the
        right, wrapping around if the rightmost column is currently
        selected.

        bad things will happen if you call this while focus isn't
        on a child of this Columns instance, probably! so don't!
        only call it from within a bindKey binding, that way it won't
        get spuriously called from random points in the code.
        """
        self.active.touch()
        self.active = self.children[index]
        self.touch()
        self.active.touch()

# good point, line 216 .. why does this work?
#        self.targetCol = index
#
#        cols = [col for col in self.columns if isinstance(col, self.Column)]
#        self.targetCol %= len(cols)
#
#        col = cols[self.targetCol]
#
#        self.engine.setFocus(col.drawable)
#
#        self.touch()


    def focus(self):
        """
        call setFocus on the correct column
        """
        cols = self.children
        if len(cols):
            child = self.active
            self.log.debug('handing focus to %s', child)
            return child.focus()
