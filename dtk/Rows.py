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
            self.weight = weight
            self.height = None 

    class Separator:
        def __init__(self, type):
            self.minheight = 1
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

        # keybindings
        self.bindKey('tab', self.switchRow)

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
            'space' leaves a blank row 1 character high
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

        # start from available height
        available = self.h

        # adjust for borders, if they're to be drawn
        if self.outerborder:
            available -= 2

            # pushes the starting x over by 1
            y += 1
            
            # outer border will also shrink our available horizontal area
            x += 1
            w -= 2

        if self.innerborder:
            available -= (len(self.rows) - 1)


        required = sum([row.minheight for row in self.rows])

        if required > available:
            raise Exception, "more space is required than available"



        totalweight = sum([row.weight for row in self.rows])
        spaceleft = available
        available -= required

        for child in self.rows:
            child.height = child.minheight + int(min(float(child.weight) / float(totalweight) * available, spaceleft))

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

        y = 0

        # 1 if true, 0 if false
        borders = int(self.outerborder) 

        for child in self.rows[:-1]:
            if isinstance(child, self.Separator) and child.type == 'line':
                self.line(0, y, self.w)

            if self.innerborder:
                self.line(0, y + borders + child.height, self.w, **attr)
                y += 1 # for ther inner border

            y += child.height

        

    def focusedRowIndex(self):
        """
        returns the index of the row in self.rows which
        has internal focus (it may not have focus as far as
        the Engine is concerned
        """
        drawable = self.getEngine().getFocusedDrawable()

        # a list of the drawables in each row
        rowdrawables = [row.drawable for row in self.rows if isinstance(row, self.Row)]

        return rowdrawables.index(drawable)

    def focusedRow(self):
        """
        returns the Row that has internal focus
        """
        return self.rows[self.getFocusedRowIndex()]


    def switchRow(self, index = None):
        """
        switches internal focus to the given row index, if it's
        in range. otherwise, switches the focused row one to the
        right, wrapping around if the rightmost row is currently
        selected.

        bad things will happen if you call this while focus isn't
        on a child of this Columns instance, probably! so don't!
        only call it from within a bindKey binding, that way it won't
        get spuriously called from random points in the code.
        """
        
        if index is None:
            index = self.focusedRowIndex()

        newindex = (index + 1) % len(self.rows)
        
        # tell engine to focus on this one
        row = self.rows[newindex]

        engine = self.getEngine()
        if engine.peekFocus() is not None:
            engine.pushFocus(row.drawable)
        else:
            engine.setFocus(row.drawable)
