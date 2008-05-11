# DTK, a curses "GUI" toolkit for Python programs.
# 
# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# 
# DTK is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# DTK is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with Foobar. If not, see <http://www.gnu.org/licenses/>.


import types

from core import Drawable
from events import SelectionChanged, HighlightChanged

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

    def __init__(self, selection = 'multiple', vimlike = False, **kwargs):
        """
        ListBox takes optional parameters 'selection' and 'vimlike':

         * selection controls the selection style - 'multiple', 'single'
           or 'none'
         * vimlike: when True enables bindings for vim-like navigation:
           j/k for up/down

        Events:
         * SelectionChanged
         * HighlightChanged
        """
        super(ListBox, self).__init__(**kwargs)

        # the higlighted element is shown in reverse mode
        self.highlighted = 0

        self.setDrawStyle()

        # these get immediately overwritten
        self.allowSelection = False
        self.multipleSelection = False
        self.selected = []
        self.items = []

        # remember the selection type
        self.setSelectionType(selection)

        # sensible defaults 
        self.firstVisible = 0

        # set up the usual keybindings
        self.bindKey('down', self.moveDown)
        self.bindKey('up', self.moveUp)
        self.bindKey('page down', self.pageDown)
        self.bindKey('page up', self.pageUp)
        if self.allowSelection:
            self.bindKey(' ', self.toggleSelect)
        self.bindKey('home', self.moveToTop)
        self.bindKey('end', self.moveToBottom)

        if vimlike:
            self.bindKey('j', self.moveDown)
            self.bindKey('k', self.moveUp)

    def __len__(self):
        return len(self.items)
    len = property(__len__)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, *args, **kwargs):
        return self.items.__getitem__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self.items.__contains__(*args, **kwargs)
    
    def _get_repr(self, item):
        """
        get the printable string for this list item. 
        if the item has defined a __dtk_str__, use that (or its return value)
        otherwise just use str(item)
        """
        str_rep = getattr(item, "__dtk_str__", None)
        if str_rep:
            if callable(str_rep): 
                str_rep = str_rep()
        else:
            str_rep = str(item)
        return str_rep

    def append(self, item):
        self.items.append(item)
        self.touch()

    def count(self, item):
        return self.items.count(item)

    def extend(self, other):
        self.items.extend(other)
        self.touch()

    def index(self, item, *args):
        """
        returns smallest i such that s[i]==x. start and
        stop limit search to only part of the list.
        """
        return self.items.index(item, *args)

    def insert(self, index, item):
        selected = []
        for elm in self.selected:
            if elm >= index:
                selected.append(elm + 1)
            else:
                selected.append(elm)
        self.selected = selected
        self.items.insert(index, item)

        self.touch()

    def pop(self, index = None):
        """
        pops the end of the list by default
        todo this should return the popped item
        """
        if index is None:
            index = len(self.items) - 1

        if index in self.selected:
            self.selected.remove(index)

        out = self.items.pop(index)
        self.touch()

        return out

    def remove(self, item):
        if self.items.index(item) in self.selected:
            self.selected.remove(self.items.index(item))
        self.items.remove(item)
        self.touch()

    def reverse(self):
        self.selected = [(len(self.items) - ix - 1) for ix in self.selected]
        self.items.reverse()
        self.touch()

    def setItems(self, items, highlighted = 0, selected = None):
        """
        sets the items list and currently highlighted item. touches
        the ListBox (forces redraw next time through drawing loop)
        """

        self.items = list(items)

        self.highlighted = highlighted
        if selected is not None:
            self.selected = selected
        else:
            self.selected = []

        self.firstVisible = 0
        self.touch()

    def move(self, index):
        """
        move the highlight to the item at given index
        """
        # since the keybinding won't know all the time how long the
        # list is, and it makes a copy of the int self.len if we were
        # to give that as the userdata
        if index == 'end':
            index = len(self.items)
            
        self.highlighted = index
        if self.highlighted < 0:
            self.highlighted = 0
        elif self.highlighted >= len(self.items):
            self.highlighted = len(self.items) - 1
            if self.highlighted < 0:
                self.highlighted = 0

        self.touch()

        self.fireEvent(HighlightChanged(self, self.items[self.highlighted]))


    def moveToTop(self):
        """
        move the highlight to the first item
        """
        self.move(0)

    def moveToBottom(self):
        """
        move the highlight to the last item
        """
        self.move(len(self.items))

    def moveUp(self):
        """
        move the highlight up one item
        """
        self.move(self.highlighted - 1)

    def moveDown(self):
        """
        move the highlight down one item
        """
        self.move(self.highlighted + 1)

    def pageDown(self):
        """
        move down by self.height rows
        """
        self.move(self.highlighted + self.h)

    def pageUp(self):
        """
        move up by self.height rows
        """
        self.move(self.highlighted - self.h)

    def getSelectedItems(self):
        """
        return a list of the selected items. order is undefined
        """
        return [self.items[i] for i in self.selected]

    def getHighlightedItem(self):
        """
        return the highlighted item
        """
        if len(self.items):
            return self.items[self.highlighted]

    # alias of getHighlightedItem
    item = getHighlightedItem

    def setSelectionType(self, selectionType):
        """
        Set the selection type for this ListBox. If changing from
        multiple selection to single selection, the existing
        selection is cleared. When changing to no selection, any
        existing selection is cleared.

        selectionType is one of 'multiple', 'single', or 'none'
        """
        selectionType = selectionType.lower()
        try:
            assert selectionType in ('multiple', 'single', 'none')
        except AssertionError:
            raise Exception("selection type must be one of multiple, single or none")

        if selectionType == 'multiple':
            self.allowSelection = True
            self.multipleSelection = True

        elif selectionType == 'single':
            # toggleSelection expects the list to have
            # at least one element -- this should not
            # cause anything to be displayed as selected
            self.selected = [None]

            self.allowSelection = True
            self.multipleSelection = False

        else:
            self.selected = []

            self.allowSelection = False
            self.multipleSelection = False


    def setDrawStyle(self, hstyle = None, sstyle = None, ustyle = None,
                     scheck = None, ucheck = None):
        """
        Set the drawing style. sstyle and ustyle are lists of drawing
        attribute keywords (eg 'bold' or 'green'). scheck and ucheck are
        strings which, if either is not none, are prepended to all
        items in the list box when drawn.

        @param hstyle: the style to be applied to the highlighted item. this
            is added to/overrides the style defined by sstyle or ustyle for
            the line which is highlighted.
        @type  sttyle: dict

        @param sstyle: the style to be applied to selected items
        @type  sttyle: dict

        @param ustyle: the style to be applied to unselected items
        @type  yttyle: dict

        @param scheck: the check mark to be applied to selected items
        @type  scheck: string

        @param ucheck: the check mark to be applied to unselected items
        @type  ucheck: string
        """
        self.hstyle = hstyle or dict(highlight=True)
        self.sstyle = sstyle or dict(bold=True)
        self.ustyle = ustyle or dict()
        self.scheck = scheck or ''
        self.ucheck = ucheck or ''

        if self.ucheck != '' or self.scheck != '':
            self.prefixlen = max([len(self.ucheck), len(self.scheck)])

            # pad them both to prefixlen with spaces
            self.scheck += ' ' * (self.prefixlen - len(self.scheck))
            self.ucheck += ' ' * (self.prefixlen - len(self.ucheck))
        else:
            self.prefixlen = 0


    def toggleSelect(self):
        """
        if the highlighted item is not selected, select it,
        and vice-versa
        """
        if not self.allowSelection:
            return

        if self.highlighted in self.selected:
            self.selected.remove(self.highlighted)

        elif self.multipleSelection:
            self.selected.append(self.highlighted)

        else:
            self.selected = [self.highlighted]

        self.touch()

        self.fireEvent(SelectionChanged(self, self.selected))

    def render(self):
        """
        if this gets called, then one of our functions has indicated
        that it's time for a redraw (through self.touch()), so we're
        going to re-draw what's in the visible range, based on our
        size and what is currently firstVisible
        """
        self.clear()

        # update firstVisible to so that currently highligted item
        # is visible
        if self.highlighted >= self.firstVisible + self.h:
            self.firstVisible = self.highlighted - self.h + 1
        elif self.highlighted < self.firstVisible:
            self.firstVisible = self.highlighted

        for i in range(self.firstVisible, min(len(self.items), self.firstVisible + self.h)):
            item = self._get_repr(self.items[i])

            if i in self.selected:
                attr = self.sstyle.copy()
                prefix = self.scheck
            else:
                attr = self.ustyle.copy()
                prefix = self.ucheck

            if self.prefixlen:
                item = prefix + item 

            if len(item) < self.w:
                item += ' ' * (self.w - len(item))

            if self.focused and i == self.highlighted:
                attr.update(self.hstyle)

            self.draw(item, i - self.firstVisible, 0, **attr);
