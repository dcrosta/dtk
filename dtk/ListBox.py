import types

from core import Drawable

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

    def __init__(self, selection = 'multiple', vimlike = False, 
                 hstyle = None, sstyle = None, ustyle = None,
                 scheck = None, ucheck = None, **kwargs):
        """
        Initialize the ListBox.

        @param parent: the parent class
        @type  parent: dtk.Drawable

        @param name: the name of this ListBox (used, eg, in logging)
        @type  name: string

        @param selection: the type of selection to be supported by this
            ListBox. one of 'multiple', 'single' or 'none'
        @type  selection: string

        @param vimlike: whether this ListBox should support vimlike
            keybindings. Currently binds 'j' to moveDown and 'k' to moveUp
        @type  vimlike: boolean

        @param hstyle: the style to be applied to the highlighted item. see
            setDrawStyle()
        @type  hstyle: dict

        @param sstyle: the style to be applied to selected items. see
            setDrawStyle()
        @type  sstyle: dict

        @param ustyle: the style to be applied to unselected items. see
            setDrawStyle()
        @type  ustyle: dict

        @param scheck: the check mark to be applied to selected items. see
            setDrawStyle()
        @type  scheck: string

        @param ucheck: the check mark to be applied to unselected items.
            see setDrawStyle()
        @type  ucheck: string
        """
        super(ListBox, self).__init__(**kwargs)

        # the higlighted element is shown in reverse mode
        self.highlighted = 0


        # these get immediately overwritten
        self.allowSelection = False
        self.multipleSelection = False
        self.selected = []
        self.items = []

        # remember the selection type
        self.setSelectionType(selection)

        # set the selection style
        self.setDrawStyle(hstyle, sstyle, ustyle, scheck, ucheck)

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
            self.selected.remove(len(self.items))
        else:
            self.selected.remove(index)
        self.items.pop(index)
        self.touch()

    def remove(self, item):
        self.selected.remove(self.index[item])
        self.items.remove(item)
        self.touch()

    def reverse(self):
        self.selected = [(len(self.items) - ix - 1) for ix in self.selected]
        self.items.reverse()
        self.touch()

    def setItems(self, items, indices = None,
                 highlighted = 0, selected = None):
        """
        sets the items list and currently highlighted item
        """

        if indices is None:
            # if indices is None, then auto-generate them
            # starting at 0
            indices = range(len(items))

        if not len(items) == len(indices):
            raise RuntimeError, 'setItems expects len(items) == len(indices)'

        # make and store a copy of the incoming items
        self.items = list(items)
        self.indices = indices

        self.highlighted = highlighted
        if selected is not None:
            self.selected = selected
        else:
            selected = [None]

        self.clear()
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


    def index(self):
        """
        return the index associated with the first highligted item
        todo this is a terrible name.
        """
        if len(self.items) == 0:
            return None
        return self.indices[self.highlighted]

    def item(self):
        """
        return the highlighted item
        todo this is a terrible name.
        """
        if len(self.items) == 0:
            return None
        return self.items[self.highlighted]
    
    def getSelectedItems(self):
        """
        return a list of the selected items
        """
        return [item for (item, index)
                in zip(self.items, range(len(self.items)))
                if index in self.selected]

    def getHighlightedItem(self):
        # todo errorcheck
        return self.items[self.highlighted]

    def setSelectionType(self, selectionType):
        """
        Set the selection type for this ListBox. If changing from
        multiple selection to single selection, the existing
        selection is cleared. When changing to no selection, any
        existing selection is cleared.

        @param selectionType: one of 'multiple', 'single', or 'none'
        """
        selectionType = selectionType.lower()
        try:
            assert selectionType in 'multiple single none'.split()
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
        if self.highlighted in self.selected:
            self.selected.remove(self.highlighted)

        elif self.multipleSelection:
            self.selected.append(self.highlighted)

        else:
            self.selected[0] = self.highlighted

        self.touch()

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
