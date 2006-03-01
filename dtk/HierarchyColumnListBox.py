import types
import utils

from TextTable import TextTable

class HierarchyColumnListBox(TextTable):
    """
    ColumnListBox extends the basic ListBox by adding support for
    a multicolumn sortable interface by accepting sequences rather
    than single items for display (each element in the sequence will
    appear in its own column, subject to layout rules, etc).
    """

    def __init__(self, parent, name, vimlike = False, spacing = 1):
        ColumnListBox.__init__(self, parent, name, spacing = spacing)

        # key bindings for heirarchical collapsing
        self.bindKey('+', self.expandAll)
        self.bindKey('-', self.collapseAll)
        self.bindKey('enter', self.expandOrCollapse)

        # state
        self.collapsed = False
        self.heirarchy = None

        self.primaryFields = []
        self.fieldNames = []

    def addColumn(self, minwidth, maxwidth = None, weight = 1, name = None, primary = False, alignment = 'left'):
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

        if name is None:
            name = 'col%s' % len(self.sizer.items)

        self.fieldNames.append(name)

        if primary:
            self.primaryFields.append(len(self.sizer.items))

        self.sizer.addItem(minwidth, maxwidth, weight, alignment = alignment)

    def collapseAll(self):
        """
        TODO: document me
        """
        self.collapsed = True

        # make it
        if self.heirarchy is None:
            self.makeHierarchy()

        self.backupitems = self.items

    def expandOrCollapse(self):
        """
        TODO: document me
        """
        pass

    def expandAll(self):
        """
        TODO: document me
        """
        self.items = self.backupitems
        self.collapsed = False

    def makeHierarchy(self):
        """
        makes the heirarchy
        """
        self.heirarchy = Node(None, -1, None)
        self.doMakeHierarchy(self.heirarchy, 0, len(self.items), 0)

        self.clear()
        self.touch()

    def doMakeHierarchy(self, parent, start, end, level):
        if level == len(self.primaryFields):
            for i in range(start, end):
                parent.addChild(Node(parent, level, self.items[i]), i, i)

        else:
            field = self.primaryFields[level]

            current = None
            s = 0
            
            for i in range(start, end):
                item = self.items[i]

                if current is None:
                    s = i
                    current = item[field]

                elif item[field] != current:
                    n = Node(parent, level, "'%s' = '%s'" % (self.fieldNames[field], current), s, i)
                    parent.addChild(n)
                    self.doMakeHierarchy(n, s, i, level + 1)

                    current = None
                    
            if current is not None:
                n = Node(parent, level, "'%s' = '%s'" % (self.fieldNames[field], current), s, end)
                parent.addChild(n)
                self.doMakeHierarchy(n, s, end, level + 1)






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


        if self.collapsed:
            self.items = []

            self.items = self.heirarchy.render()


        # update firstVisible to so that currently highligted item
        # is visible
        if self.highlighted >= self.firstVisible + self.h:
            self.firstVisible = self.highlighted - self.h + 1
        elif self.highlighted < self.firstVisible:
            self.firstVisible = self.highlighted

        for i in range(self.firstVisible, min(len(self.items), self.firstVisible + self.h)):
            item = self.items[i]

            if isinstance(item, Node):
                item = item.data

            if type(item) is types.TupleType or type(item) is types.ListType:
                if len(item) < self.cols:
                    item += ' ' * (len(item) - self.cols)
                elif len(item) > self.cols:
                    item = [item[i] for i in range(self.cols)]
    
                formatted = self.format % tuple(item)

            elif type(item) is types.StringType:
                formatted = item
    
            attr = {}
            if i in self.selected:
                attr['bold'] = True
            if self.focused and i == self.highlighted:
                attr['highlight'] = True


            self.draw(formatted, i - self.firstVisible, 0, **attr);


class Node:
    """
    represents a node in the heirarchy tree
    """

    def __init__(self, parent, level, data, start, end):
        self.parent = parent
        self.level = level
        self.data = data

        self.children = []

        self.collapsed = True

        self.start = start
        self.end = end

    def __str__(self):
        return str(self.data)

    def addChild(self, child):
        self.children.append(child)

    def highlighted(self, highlighted, state = 'normal'):
        """
        recursively determine which Node is or contains the
        highligted element. state is either 'normal' which indicates
        that the highlighted index is relative to the (partially) collapsed
        Node tree, or 'initial' which indicates that the index
        is relative to the original list.
        """

        if state == 'normal':
            pass

        elif state == 'initial':
            if not self.collapsed:
                if highlighted == self.start and highlighted == self.end:
                    #return 
                    pass

        


    def render(self):
        """
        return a string to be rendered. if the node is collapsed,
        then it returns a descriptive string to be displayed, else
        it displays the string of the underlying stuff
        """
        c = len(self.children)

        if c == 0:
            if self.collapsed:
                return []
            else:
                return [self]

        else:
            out = []
            if self.level != -1:
                prefix = '  ' * self.level
                if self.collapsed:
                    prefix += '+'
                out = ["%s %s, %d items" % (prefix, self.data, c)]

            for child in self.children:
                out.extend(child.render())

            return out

