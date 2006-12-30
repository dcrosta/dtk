from Label import Label

class Button(Label):
    """
    Similar to Label, but with some added keybindings.

    Supports the 'click' pseudo-keystroke for binding
    actions to the click action on the button (default
    hitting <enter>)
    """

    def __init__(self, text = None, decoration = '[%s]', **kwargs):
        super(Button, self).__init__(text, **kwargs)

        self.setDecoration(decoration)
        self.bindKey('enter', self._doClick)


    def setDecoration(self, decoration):
        """
        sets the 'button decoration'. this should
        be a format string with a single string
        format conversion.
        """
        self.decoration = decoration


    def _doClick(self):
        """
        Call parent's handleInput() method with the
        'click' pseudo-key
        """
        super(Button, self).handleInput('click')


    def render(self):
        """
        Draw the text formatted with the decoration. If
        focused, we draw with the highlight attribute
        (usually reverse-colors)
        """
        self.draw(self.decoration % self.text, 0, 0, highlight = self.focused)
