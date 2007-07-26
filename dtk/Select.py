# Copyright (C) 2006-2007 Dan Crosta
# Copyright (C) 2006-2007 Ethan Jucovy
# Some rights reserved.
# 
# DTK is licensed under the Creative Commons Attribution-ShareAlike 3.0 US
# license. Under this license you are free:
# 
#   * to Share -- to copy, distribute, display, and perform the work
#   * to Remix -- to make derivative works
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
