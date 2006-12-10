from Drawable import Drawable
import curses

class Rows(Drawable):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the row, or both.
    """

    class Row:
        def __init__(self, drawable, minheight, maxheight, weight):
            self.drawable = drawable
            self.minheight = minheight
            self.maxheight = maxheight
            self.weight = float(weight)
            self.height = None 

    class Separator:
        def __init__(self, type):
            self.minheight = 1
            self.maxheight = 1
            self.height = 1 
            self.weight = 0
            self.type = type


    def __init__(self, parent, name, outerborder = True, innerborder = True):
        """
        initialize the ColumnLayout
        """
        super(Rows, self).__init__(parent, name)

        # save these for later use
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

    def addRow(self, drawable, minheight, maxheight = None, weight = 1):
        """
        add a row (will become the bottom row) containing
        the given drawable (its parent should be this ColumnLayout),
        which will be drawn with the appropriate minimum and
        maximum height, as space allows. weight is used to calculate
        how to distribute remaining space after minimum and maximum
        are taken into account.
        """
        self.rows.append(self.Row(drawable, minheight, maxheight, weight))
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

    def insertRow(self, index, drawable, minheight, maxheight = None, weight = 1):
        """
        same mechanics as addRow, but it inserts it in the indexth
        position in the row list. if index > num rows, it will
        be the bottom; if index < 0, it will be the top
        row. the indices are not stored, so:

        rows.addRow(foo, ...)
        rows.insertRow(bar, 10, ...)
        rows.insertRow(baz, 5, ...)

        will result in the row ordered foo, bar, baz from left-
        to-right. (that is, the insertion works as it would on any
        ordinary python list)

        weight is used to calculate how to distribute remaining space
        after minimum and maximum are taken into account.
        """
        self.rows.insert(index, self.Row(drawable, minheight, maxheight, weight))
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


        required = sum([row.minheight for row in self.rows])

        maxheights = [row.maxheight for row in self.rows]
        if None not in maxheights:
            most = sum([row.maxheight for row in self.rows])
        else:
            most = available


        if required > available:
            raise Exception, "more space is required than available"

        if most < available:
            self.log.debug('sum of max heights less than available space, using those heights')

            for row in self.rows:
                child.height = child.maxheight

        else:
            totalweight = float(sum([row.weight for row in self.rows]))
            spaceleft = available
            available -= required

            for child in self.rows:
                if totalweight > 0:
                    child.height = child.minheight + int(min(child.weight / totalweight * available, spaceleft, child.maxheight or available))
                else:
                    child.height = child.minheight
    
                if isinstance(child, self.Row):
                    child.drawable.setSize(y, x, child.height, w)
    
                y += child.height
                if self.innerborder:
                    y += 1
    
                spaceleft -= child.height
    
            # find the last row which has a Drawable,
            # and add remaining space to that row
            index = max([index for index in range(len(self.rows)) if isinstance(self.rows[index], self.Row)])
            if spaceleft:
                self.rows[index].height += spaceleft
                # dangerous, maybe
                self.rows[index].drawable.h += spaceleft


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
            self.log.debug('@%2d child is %s' % (y, child))
            if isinstance(child, self.Separator):
                if child.type == 'line':
                    self.line(borders, y, self.w - 2 * borders)
                elif child.type == 'space':
                    self.draw(' ' * (self.w - 2 * borders), y, borders)

            y += child.height or 0

            if self.innerborder:
                self.line(0, y, self.w, **attr)
                y += 1 # for ther inner border


    def nextRow(self):
        self.switchRow(self.targetRow + 1)


    def prevRow(self):
        self.switchRow(self.targetRow - 1)
        

    def switchRow(self, index):
        """
        TODO
        """
        self.log.debug('switching row from %s to %s' % (self.targetRow, index))
        self.targetRow = index 
        
        # tell engine to focus on this one
        rows = [row for row in self.rows if isinstance(row, self.Row)]

        self.targetRow %= len(rows) 
        row = rows[self.targetRow]

        engine = self.getEngine()
        if engine.peekFocus() is not None:
            engine.pushFocus(row.drawable)
        else:
            engine.setFocus(row.drawable)

        self.touch()
