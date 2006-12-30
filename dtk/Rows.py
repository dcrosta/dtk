from Drawable import Drawable
import curses
import util

class Rows(Drawable):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the row, or both.
    """

    class Row:
        def __init__(self, drawable, fixedsize, weight):
            self.drawable = drawable
            self.fixedsize = fixedsize
            self.weight = float(weight)
            self.height = None 

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

        # the row definitions
        self.rows = []

        # the row we're currently targeted on
        self.targetRow = 0

        # keybindings
        self.bindKey('tab', self.nextRow)

    def __str__(self):
        return 'Rows'


    def handleInput(self, input):
        """
        Pass input to the current row
        """
        consumed = self.rows[self.targetRow].drawable.handleInput(input)
        if not consumed:
            consumed = super(Rows, self).handleInput(input)

        return consumed
    

    def addRow(self, drawable, fixedsize = None, weight = 1):
        """
        add a row (will become the bottom row) containing
        the given drawable (its parent should be this ColumnLayout),
        which will be drawn with the appropriate minimum and
        maximum height, as space allows. weight is used to calculate
        how to distribute remaining space after minimum and maximum
        are taken into account.
        """
        self.rows.append(self.Row(drawable, fixedsize, weight))
        self.touch()

    def addSeparator(self, type = 'line'):
        """
        adds a 'separator row', which contains a horizontal line
        akin to those drawn when internal borders are enabled.

        @param type: 'line' draws a horizontal line like the borders;
            'blank' leaves a blank row 1 character high
        @type  type: string
        """
        self.rows.append(self.Separator(type))
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
        self.rows.insert(index, self.Row(drawable, fixedsize, weight))
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


        items = [(item.fixedsize, item.weight) for item in self.rows]

        sizes = util.flexSize(items, available)

        for (child, size) in zip(self.rows, sizes):
            child.height = size

            if isinstance(child, self.Row):
                self.log.debug('setting size of "%s" to (%d, %d, %d, %d)', child.drawable.name, y, x, child.height, w)
                child.drawable.setSize(y, x, child.height, w)

            y += child.height
            if self.innerborder:
                y += 1


    def drawContents(self):
        """
        call drawContents() on each of our children
        """
        for child in self.rows:
            if isinstance(child, self.Row):
                child.drawable.drawContents()

        # draw borders through render()
        super(Rows, self).drawContents()

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

        for child in self.rows[:-1]:
            if isinstance(child, self.Separator):
                if child.type == 'line':
                    self.line(y, borders, self.w - 2 * borders)
                elif child.type == 'blank':
                    self.draw(' ' * (self.w - 2 * borders), borders, y)

            y += child.height or 0

            if self.innerborder:
                self.line(y, 0, self.w, **attr)
                y += 1 # for ther inner border


    def nextRow(self):
        self.switchRow(self.targetRow + 1)


    def prevRow(self):
        self.switchRow(self.targetRow - 1)
        

    def switchRow(self, index):
        self.log.debug('switching row from %s to %s' % (self.targetRow, index))
        self.targetRow = index 
        
        # tell engine to focus on this one
        rows = [row for row in self.rows if isinstance(row, self.Row)]
        if len(rows):
            self.targetRow %= len(rows) 

            self.engine.setFocus(rows[self.targetRow].drawable)
            self.touch()


    def focus(self):
        """
        call setFocus on the correct row
        """
        rows = [row for row in self.rows if isinstance(row, self.Row)]
        if len(rows):
            child = rows[self.targetRow].drawable
            self.log.debug('handing focus to %s', child)
            return child.focus() 
