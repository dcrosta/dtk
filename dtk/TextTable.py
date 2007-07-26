# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# All rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share to copy, distribute, display, and perform the work
#   * to Remix to make derivative works
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


import types
import util

from ListBox import ListBox

class TextTable(ListBox):
    """
    TextTable extends the basic ListBox by adding support for
    a multicolumn sortable interface by accepting sequences rather
    than single items for display (each element in the sequence will
    appear in its own column, subject to layout rules, etc).
    """

    class TextColumn:
        def __init__(self, fixedsize, weight, alignment):
            self.fixedsize = fixedsize
            self.weight = weight
            self.alignment = alignment
            self.width = None

    def __init__(self, spacing = 1, **kwargs):
        super(TextTable, self).__init__(**kwargs)

        self.colnames = []

        self.spacing = spacing

        self.format = None
        self.cols = []

    def setSize(self, y, x, h, w):
        """
        clear the column cache, then call ListBox.setSize()
        """
        self.format = None

        ListBox.setSize(self, y, x, h, w)

    def addColumn(self, fixedsize = None, weight = 1, alignment = 'left', name = None):
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

        self.cols.append(self.TextColumn(fixedsize, weight, alignment))
        self.colnames.append(name)

        self.touch()


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

            availwidth = self.w - ((len(self.cols) - 1) * self.spacing)

            sizeitems = [(c.fixedsize, c.weight) for c in self.cols]
            sizes = util.flexSize(sizeitems, availwidth)

            for (col, size) in zip(self.cols, sizes):
                col.width = size

                self.format += '%'
                if col.alignment == 'left':
                    self.format += '-'
                self.format += ('%d' % col.width) + ('.%d' % col.width) + 's'
                self.format += ' ' * self.spacing

            # trim off trailing space
            if self.spacing:
                self.format = self.format[:len(self.format) - self.spacing]

        offset = 0
        
        # max([None, None, ...]) will evaluate False
        if max(self.colnames):
            # then we must render the header
            self.draw(self.format % tuple(map(lambda x: x or '', self.colnames)), 0, 0, bold = True)
            self.line(1, 0, self.w)

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

            if len(item) < len(self.cols):
                item = list(item)
                item.extend([''] * (len(self.cols) - len(item)))

            elif len(item) > len(self.cols):
                item = item[:len(self.cols)]

            attr = {}
            if i in self.selected:
                attr['bold'] = True
            if self.focused and i == self.highlighted:
                attr['highlight'] = True

            formatted = self.format % tuple(item)

            self.draw(formatted, i - self.firstVisible + offset, 0, **attr);
