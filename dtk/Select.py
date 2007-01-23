from core import Drawable

class Select(Drawable):
    """
    Select is a widget which looks like a button when
    unfocused, and shows a horizontal list of choices
    when focused. The list will take up as much room as
    is available to be drawn or as is needed.

    The left and right keys will move the selection on
    the Select (each time firing the 'selection changed'
    event), but the user must hit Enter to choose an
    option (this will fire the 'clicked') event.

    The selected/highlighted item will be shown in reverse
    colors; the chosen item (which may be different than
    the selected item when the user moves the selection
    but hasn't hit enter) will be bold.

    Events:
     * 'selection changed' when the selection changes
     * 'clicked' when the user hits enter on an option
    """


    def __init__(self, **kwargs):
        super(Select, self).__init__(**kwargs)

        self.items = []
        self.chosen = None
        self.selected = None

        self.bindKey('right', self.selectNext)
        self.bindKey('left', self.selectPrev)
        self.bindKey('enter', self.clicked)


    def setItems(self, items):
        self.items = items
        self.touch()

        if self.selected is None:
            self.selected = 0


    def setChosenItem(self, item):
        """
        make the given item the chosen one if it is
        in the list of items
        """
        if item in self.items:
            self.chosen = self.items.index(item)
            self.touch()


    def getChosenItem(self):
        """
        return the chosen item
        """
        return self.chosen
    

    def clicked(self):
        """
        set the chosen item to the currently highlighted one,
        and fire the 'clicked' event
        """
        self.chosen = self.selected
        self.touch()

        self.fireEvent('clicked')


    def selectNext(self):
        """
        move the selection one to the right, wrapping
        around to the beginning if necessary
        """
        if self.selected is None:
            self.selected = self.items[0]

        else:
            self.selected = (self.selected + 1) % len(self.items)

        self.touch()

        self.fireEvent('selection changed')


    def selectPrev(self):
        """
        move the selection one to the left, wrapping
        around to the beginning if necessary
        """
        if self.selected is None:
            self.selected = self.items[0]

        else:
            self.selected = (self.selected - 1) % len(self.items)

        self.touch()

        self.fireEvent('selection changed')


    def render(self):
        self.clear()
        
        size = sum([len(item) for item in self.items]) + len(self.items) + 3

        selected_item = None
        chosen_item = None
        if len(self.items) > 0:
            selected_item = self.items[self.selected]
        if self.chosen is not None:
            chosen_item = self.items[self.chosen]

        # cache this for efficiency
        focused = self.focused 

        if self.w >= size:
            self.draw('[', 0, 0)
            x = 2
            for item in self.items:
                self.draw(item, 0, x, highlight = (focused and item == selected_item), bold = (item == chosen_item))
                x += len(item) + 1

            self.draw(']', 0, x)

        else:
            self.draw('[ %s ]' % selected_item, 0, 0, highlight = focused, bold = chosen_item == selected_item)
