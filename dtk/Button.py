from Label import Label

class Button(Label):
    """
    Button is a clickable widget which is displayed with
    customizable decoration. 'enter' is bound to the click
    action which fires the 'clicked' event.

    Events (in addition to standard Drawable events):
     * 'clicked' when the user "clicks" the button (hitting enter)
    """

    def __init__(self, text = None, decoration = '[%s]', **kwargs):
        super(Button, self).__init__(text, **kwargs)

        self.setDecoration(decoration)
        self.bindKey('enter', self.fireEvent, 'clicked')


    def setDecoration(self, decoration):
        """
        sets the 'button decoration'. this should
        be a format string with a single string
        format conversion.
        """
        self.decoration = decoration


    def render(self):
        """
        Draw the text formatted with the decoration. If
        focused, we draw with the highlight attribute
        (usually reverse-colors)
        """
        self.draw(self.decoration % self.text, 0, 0, highlight = self.focused)
