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
        """
        struct class
        """

        def __init__(self, drawable, minheight, maxheight, weight):
            self.drawable = drawable
            self.minheight = minheight
            self.maxheight = maxheight
            self.weight = weight
            self.height = None 

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
        self.setSize(self.y, self.x, self.h, self.w)
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
        self.setSize(self.y, self.x, self.h, self.w)
        self.touch()


    def setRow(self, index, drawable, minheight, maxheight = None, weight = 1):
        """
        similar to insertRow, but will overwrite a row that already
        exists with the given index.
        """
        self.rows[index].drawable.clear()

        self.rows[index] = self.Row(drawable, minheight, maxheight, weight)
        self.setSize(self.y, self.x, self.h, self.w)
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

            child.drawable.setSize(y, x, child.height, w)

            y += child.height
            if self.innerborder:
                y += 1

            spaceleft -= child.height

        # fudge the last row
        if spaceleft:
            self.rows[-1].height += spaceleft
            # dangerous, maybe
            self.rows[-1].drawable.h += spaceleft



    def drawContents(self):
        """
        call drawContents() on each of our children
        """
        for child in self.rows:
            child.drawable.drawContents()

        # draw borders through render()
        self.render()

    def render(self):
        """
        draw the borders
        """
        if self.outerborder:
            self.box(0, 0, self.w, self.h)

        if self.innerborder:
            y = 0

            # 1 if true, 0 if false
            borders = int(self.outerborder) 

            for child in self.rows[:-1]:
                if self.outerborder:
                    self.line(0, y + borders + child.height, self.w, leftEnd = curses.ACS_LTEE, rightEnd = curses.ACS_RTEE)
                else:
                    self.line(0, y + child.height, self.w)

                y += child.height
                borders += 1

        

    def focusedRowIndex(self):
        """
        returns the index of the row in self.rows which
        has internal focus (it may not have focus as far as
        the Engine is concerned
        """
        drawable = self.getEngine().getFocusedDrawable()

        # a list of the drawables in each row
        rowdrawables = [row.drawable for row in self.rows]

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
