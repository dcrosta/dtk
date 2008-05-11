
__all__ = ['Event', 'SelectionChanged', 'HighlightChanged', 'Clicked', 'TextChanged', 'Resized']

class Event(object):
    """
    the base event type. contains a public attribute `source`
    which is a reference to the widget which fired the event.
    """

    def __init__(self, source):
        self.source = source

class SelectionChanged(Event):
    """
    Fired by a Widget whenever the user changes the selection.
    The public attribute `selection` contains the list of
    currently selected items. It may be of length 0.
    """
    def __init__(self, source, selection):
        Event.__init__(self, source)
        self.selection = selection

class HighlightChanged(Event):
    """
    Fired by a Widget whenever the user moves the highlight
    cursor. The public attribute `higlight` contains the
    currently highlighted item.
    """
    def __init__(self, source, highlight):
        Event.__init__(self, source)
        self.highlight = highlight

class Clicked(Event):
    """
    Fired by a Widget when the user "clicks" the widget. This
    means something like pressing <enter> when focused on
    a Button.
    """
    pass

class TextChanged(Event):
    """
    Fired by a text-holding Widget when its text changes due
    to user input (ie, not if the program code calls setText()
    or similar on the widget). The public attribute `text`
    contains the current text of the widget, as a string
    (possibly with newline characters).
    """
    def __init__(self, source, text):
        Event.__init__(self, source)
        self.text = text

class Resized(Event):
    """
    Fired by a Widget when it is resized. Ordinarily, this is
    because the size of the terminal changed, but it can also
    be due to its parent Container's parameters changing.
    """
    def __init__(self, source, width, height):
        Event.__init__(self, source)
        self.width = width
        self.height = height
