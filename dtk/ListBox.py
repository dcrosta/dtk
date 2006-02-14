import types

from Drawable import Drawable

class ListBox(Drawable):
    """
    ListBox displays a list of items, and supports a visible 
    cursor (for user interaction) as well as a variable number of
    selected items.
    
    It implements (most of) the list interface for
    many operations, but these *do not* operate on the list of
    items you are displaying, nor will changing that list make all
    the changes necessary to update the display as it should be.
    Basically, whatever you do to that list (inserting, appending
    or deleting items, say) you should also do to the ListBox that
    views the list.
    """

    def __init__(self, parent, name, vimlike = False):
        Drawable.__init__(self, parent, name)

        # the higlighted element is shown in reverse mode
        self.highlighted = 0

        # selected is a list to support selecting
        # ranges or several individual elements
        self.selected = []

        # sensible defaults 
        self.firstVisible = 0

        # set up the usual keybindings
        self.bindKey('down', self.moveDown)
        self.bindKey('up', self.moveUp)
        self.bindKey('page down', self.pageDown)
        self.bindKey('page up', self.pageUp)
        self.bindKey('space', self.toggleSelect)
        self.bindKey('home', self.moveToTop)
        self.bindKey('end', self.moveToBottom)

        if vimlike:
            self.bindKey('j', self.moveDown)
            self.bindKey('k', self.moveUp)


    # to conform, roughly, to the list interface
    def __contains__(self, item):
        """
        we'll hand this off to the underlying data
        """
        return item in self.items

    def __delitem__(self, key):
        """
        check if we need to deal with the selected or highlighted items
        """

        if type(key) == types.SliceType:
            step = key.step or 1
            for i in range(key.start, key.stop, step):
                self.__delitem__(i)

        elif type(key) == types.IntType:
            if key in self.selected:
                self.selected.remove(key)

            if key == self.highlighted:
                self.highlighted -= 1

            self.len -= 1
            if self.len < 0:
                self.len = 0

            self.touch()

        else:
            raise ValueError, "unknown key type: %s" % type(key)


    def __getitem__(self, key):
        return self.items[key]

    def __iadd__(self, other):
        """
        concatenation, like extend()
        """
        self.len += len(other)
        self.touch()

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return self.len

    def __setitem__(self, key, item):
        raise Exception, "not implemented yet"

    def append(self, item):
        """
        check if we need to deal with the selected or highlighted items
        """
        self.len += 1
        self.touch()

    def count(self, item):
        """
        returns number of i's for which self[i] == item
        """
        return self.items.count(item)

    def extend(self, other):
        """
        we just use the __iadd__ operator
        """
        self += other
        self.touch()

    def index(self, item, *args):
        """
        returns smallest i such that s[i]==x. start and
        stop limit search to only part of the list.
        """
        return self.items.index(item, *args)

    def insert(self, index, item):
        self.len += 1

        selected = []
        for elm in self.selected:
            if elm >= index:
                selected.append(elm + 1)
            else:
                selected.append(elm)

        self.selected = selected

        self.touch()

    def pop(self, index = None):
        """
        pops the end of the list by default
        """
        self.len -= 1
        if index is None:
            self.selected.remove(self.len)
        else:
            self.selected.remove(index)

        self.touch()

    def remove(self, item):
        self.len -= 1
        self.selected.remove(self.index[item])

        self.touch()

    def reverse(self):
        self.selected = [(self.len - ix - 1) for ix in self.selected]

        self.touch()

    def setItems(self, items, indices = None, highlighted = 0, selected = None):
        """
        sets the items dict and currently highlighted item
        """

        if indices is None:
            # if indices is None, then auto-generate them
            # starting at 0
            indices = range(len(items))

        if not len(items) == len(indices):
            raise RuntimeError, 'setItems expects len(items) == len(indices)'

        self.items = items
        self.indices = indices
        self.len = len(self.items)

        self.highlighted = highlighted
        if selected is not None:
            self.selected = selected

        self.touch()

    def move(self, index):
        """
        move the highlight to the item at given index
        """
        # since the keybinding won't know all the time how long the
        # list is, and it makes a copy of the int self.len if we were
        # to give that as the userdata
        if index == 'end':
            index = self.len
            
        self.highlighted = index
        if self.highlighted < 0:
            self.highlighted = 0
        elif self.highlighted >= self.len:
            self.highlighted = self.len - 1
            if self.highlighted < 0:
                self.highlighted = 0

        self.touch()


    def moveToTop(self):
        """
        move the highlight to the first item
        """
        self.move(0)
        self.touch()

    def moveToBottom(self):
        """
        move the highlight to the last item
        """
        self.move(self.len)
        self.touch()

    def moveUp(self):
        """
        move the highlight up one item
        """
        self.move(self.highlighted - 1)
        self.touch()

    def moveDown(self):
        """
        move the highlight down one item
        """
        self.move(self.highlighted + 1)
        self.touch()

    def pageDown(self):
        """
        move down by self.height rows
        """
        self.move(self.highlighted + self.h)
        self.touch()

    def pageUp(self):
        """
        move up by self.height rows
        """
        self.move(self.highlighted - self.h)
        self.touch()


    def __len__(self):
        return self.len

    def __getitem__(self, n):
        return self.items[n]

    def index(self):
        """
        return the index associated with the first highligted item
        """
        if self.len == 0:
            return None
        return self.indices[self.highlighted]

    def item(self):
        """
        return the highlighted item
        """
        if self.len == 0:
            return None
        return self.items[self.highlighted]

    def toggleSelect(self):
        """
        if the highlighted item is not selected, select it,
        and vice-versa
        """
        if self.highlighted in self.selected:
            self.selected.remove(self.highlighted)
        else:
            self.selected.append(self.highlighted)

        self.touch()

    def gotFocus(self):
        """
        when we get focus, 
        """
        Drawable.gotFocus(self)
        self.hideCursor()
        self.touch()

    def lostFocus(self):
        """
        when we lose focus, 
        """
        Drawable.lostFocus(self)
        self.touch()

    def render(self):
        """
        if this gets called, then one of our functions has indicated
        that it's time for a redraw (through self.touch()), so we're
        going to re-draw what's in the visible range, based on our
        size and what is currently firstVisible
        """

        # update firstVisible to so that currently highligted item
        # is visible
        if self.highlighted >= self.firstVisible + self.h:
            self.firstVisible = self.highlighted - self.h + 1
        elif self.highlighted < self.firstVisible:
            self.firstVisible = self.highlighted

        for i in range(self.firstVisible, min(len(self.items), self.firstVisible + self.h)):
            item = self.items[i]

            if len(item) < self.w:
                item += ' ' * (self.w - len(item))

            attr = {}
            if i in self.selected:
                attr['bold'] = True
            if self.hasFocus and i == self.highlighted:
                attr['highlight'] = True

            self.draw(item, i - self.firstVisible, 0, **attr);
