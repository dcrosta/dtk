from Drawable import Drawable
import curses

class Columns(Drawable):
    """
    implements a flexible, resizable (hopefully!) layout
    scheme for Drawables. Supports a border option, which
    will draw a one-character border around the whole area,
    or between the columns, or both.
    """

    class Column:
        """
        struct class
        """

        def __init__(self, drawable, minwidth, maxwidth, weight):
            self.drawable = drawable
            self.minwidth = minwidth
            self.maxwidth = maxwidth
            self.weight = weight
            self.width = None 

    def __init__(self, parent, name, outerborder = True, innerborder = True):
        """
        initialize the ColumnLayout
        """
        super(Columns, self).__init__(parent, name)

        # save these for later use
        self.outerborder = outerborder
        self.innerborder = innerborder

        # the column definitions
        self.columns = []

        # keybindings
        self.bindKey('tab', self.switchColumn)

    def __str__(self):
        return 'Columns'

    def addColumn(self, drawable, minwidth, maxwidth = None, weight = 1):
        """
        add a column (will become the rightmost column) containing
        the given drawable (its parent should be this ColumnLayout),
        which will be drawn with the appropriate minimum and
        maximum width, as space allows. weight is used to calculate
        how to distribute remaining space after minimum and maximum
        are taken into account.
        """
        self.columns.append(self.Column(drawable, minwidth, maxwidth, weight))

    def insertColumn(self, index, drawable, minwidth, maxwidth = None, weight = 1):
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
        self.columns.insert(index, self.Column(drawable, minwidth, maxwidth, weight))

    def setSize(self, y, x, h, w):
        """
        calculate children's sizes, then call setSize on each of them
        """
        super(Columns, self).setSize(y, x, h, w)

        # start from available width
        available = self.w

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


        required = sum([col.minwidth for col in self.columns])

        if required > available:
            raise Exception, "more space is required than available"



        totalweight = sum([col.weight for col in self.columns])
        spaceleft = available
        available -= required

        for child in self.columns:
            child.width = child.minwidth + int(min(float(child.weight) / float(totalweight) * available, spaceleft))

            child.drawable.setSize(y, x, h, child.width)

            x += child.width
            if self.innerborder:
                x += 1

            spaceleft -= child.width

        # fudge the last column
        if spaceleft:
            self.columns[-1].width += spaceleft
            # dangerous, maybe
            self.columns[-1].drawable.w += spaceleft



    def drawContents(self):
        """
        call drawContents() on each of our children
        """
        for child in self.columns:
            child.drawable.drawContents()

        # draw borders through render() if necessary
        super(Columns, self).drawContents()

    def render(self):
        """
        draw the borders
        """
        if self.outerborder:
            self.box(0, 0, self.w, self.h)

        if self.innerborder:
            x = self.x

            # 1 if true, 0 if false
            borders = int(self.outerborder) 

            for child in self.columns[:-1]:
                if self.outerborder:
                    self.lineDown(x + borders + child.width, self.y, self.h, topEnd = curses.ACS_TTEE, bottomEnd = curses.ACS_BTEE)
                else:
                    self.lineDown(x + borders + child.width, self.y, self.h)

                x += child.width
                borders += 1


    def focusedColumnIndex(self):
        """
        returns the index of the column in self.columns which
        has internal focus (it may not have focus as far as
        the Engine is concerned
        """
        drawable = self.getEngine().getFocusedDrawable()

        # a list of the drawables in each column
        coldrawables = [col.drawable for col in self.columns]

        return coldrawables.index(drawable)

    def focusedColumn(self):
        """
        returns the Column that has internal focus
        """
        return self.columns[self.getFocusedColumnIndex()]

    def switchColumn(self, index = None):
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
        
        if index is None:
            index = self.focusedColumnIndex()

        newindex = (index + 1) % len(self.columns)
        
        # tell engine to focus on this one
        col = self.columns[newindex]

        engine = self.getEngine()
        if engine.peekFocus() is not None:
            engine.pushFocus(col.drawable)
        else:
            engine.setFocus(col.drawable)
