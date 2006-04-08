from Drawable import Drawable

class Label(Drawable):
    """
    Label is a static text area that can be changed, but which provies no
    particular means for input. It's an un-editable bit of text, that's
    all.

    For now, Label only handles a single line of text -- this might need
    to change at some later point.
    """

    def __init__(self, parent, name, text = None):
        super(Label, self).__init__(parent, name)

        if text is None:
            self.text = name
        else:
            self.text = text


    def getText(self):
        """
        sets the Label's text to be the given text
        """
        return self.text


    def setText(self, text):
        """
        sets the Label's text to be the given text
        """
        self.text = text
        self.clear()
        self.touch()


    def render(self):
        """
        simply draw the text we have starting at the first position, and
        going on for as long as we can (Engine enforces clipping of the text
        string)
        """
        self.draw(self.text, 0, 0)

