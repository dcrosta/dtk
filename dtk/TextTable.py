import types
import util

from ListBox import ListBox

class TextTable(ListBox):
    """
    ColumnListBox extends the basic ListBox by adding support for
    a multicolumn sortable interface by accepting sequences rather
    than single items for display (each element in the sequence will
    appear in its own column, subject to layout rules, etc).
    """

    def __init__(self, parent, name, spacing = 1, **kwargs):
        super(TextTable, self).__init__(parent, name, **kwargs)

        # this guy calculates our columns for us (easy!)
        self.sizer = util.FlexSizer(spacing)
        self.colnames = []

        self.spacing = spacing

        self.format = None
        self.cols = 0

    def setSize(self, y, x, h, w):
        """
        clear the column cache, then call ListBox.setSize()
        """
        self.format = None
        self.cols = 0

        ListBox.setSize(self, y, x, h, w)

    def addColumn(self, minwidth, maxwidth = None, weight = 1, alignment = 'left', name = None):
        """
        add a column (will become the rightmost column) containing
        the given drawable (its parent should be this ColumnLayout),
        which will be drawn with the appropriate minimum and
        maximum width, as space allows. weight is used to calculate
        how to distribute remaining space after minimum and maximum
        are taken into account. alignment may be one of 'left' or 'right'
        """
        if alignment != 'left' and alignment != 'right':
            raise ValueError, "'alignment' argument must be 'left' or 'right'"

        self.sizer.addItem(minwidth, maxwidth, weight, sortOrder = None, sortPriority = None, alignment = alignment)
        self.colnames.append(name)

    def render(self):
        """
        if this gets called, then one of our functions has indicated
        that it's time for a redraw (through self.touch()), so we're
        going to update and return the window object for the Engine to
        draw.
        """

        # figure out column widths
        if self.format is None:
            self.format = ''

            cols = self.sizer.calculate(self.w)
            self.cols = len(cols)

            for col in cols:
                self.format += '%'
                if col.alignment == 'left':
                    self.format += '-'
                self.format += ('%d' % col.size) + ('.%d' % col.size) + 's'
                self.format += ' ' * self.spacing

            # trim off trailing space
            if self.spacing:
                self.format = self.format[:len(self.format) - self.spacing]

        offset = 0
        
        # max([None, None, ...]) will evaluate False
        if max(self.colnames):
            # then we must render the header
            self.draw(self.format % tuple(map(lambda x: x or '', self.colnames)), 0, 0, bold = True)
            self.line(0, 1, self.w)

            offset = 2
        
        # the effective height, less the offset (if there's a header)
        height = self.h - offset

        # update firstVisible to so that currently highligted item
        # is visible
        if self.highlighted >= self.firstVisible + height:
            self.firstVisible = self.highlighted - height + 1
        elif self.highlighted < self.firstVisible:
            self.firstVisible = self.highlighted

        for i in range(self.firstVisible, min(len(self.items), self.firstVisible + height)):
            item = self.items[i]

            if len(item) < self.cols:
                item += ' ' * (len(item) - self.cols)
            elif len(item) > self.cols:
                item = [item[i] for i in range(self.cols)]

            attr = {}
            if i in self.selected:
                attr['bold'] = True
            if self.focused and i == self.highlighted:
                attr['highlight'] = True

            formatted = self.format % tuple(item)

            self.draw(formatted, i - self.firstVisible + offset, 0, **attr);
