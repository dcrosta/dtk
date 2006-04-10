import types
import math

import util
from Drawable import Drawable

class Dialog(Drawable):
    """
    Dialog is the base class for popup notifications
    that should float on top of the other Drawables and
    will have focus for as long as it is visible (ie,
    all Dialogs are modal).

    Dialog has a single "OK" button, used to dismiss
    the box.

    Dialog will try to draw itself to a 4x3-ish ratio
    in the middle of the screen. Its behavior is undefined
    if the text to be shown plus the button take up more
    space than is available -- be smart! The text will
    be re-wrapped to fit in the available space.
    """

    def __init__(self, parent, name, title = None, text = None):
        """
        Dialog constructor.

        @param parent: the parent Drawable
        @type  parent: dtk.Drawable

        """
        super(Dialog, self).__init__(parent, name)

        self.setTitle(text)
        self.setText(text)


    def setText(self, text):
        """
        sets the text for the dialog

        @param text: the text to be displayed. this may be
            a string or a sequence of strings, in which
            case each string is displayed as a "paragraph"
            with a blank line between
        @type  text: string or list of strings
        """
        self.text = text
        self.touch()


    def getText(self):
        """
        returns the text currently assigned to this Dialog

        @return: the text
        @rtype:  string or list of strings
        """
        return self.text


    def setTitle(self, title):
        """
        sets the title for the dialog

        @param title: the title to be displayed. this may be
            a string or a sequence of strings, in which
            case each string is displayed as a "paragraph"
            with a blank line between
        @type  title: string or list of strings
        """
        self.title = title
        self.touch()


    def getTitle(self):
        """
        returns the title currently assigned to this Dialog

        @return: the title
        @rtype:  string or list of strings
        """
        return self.title


    def clickedOK(self):
        self.log('calling popFocus(%s)' % self)
        self.getEngine().popFocus(self)


    def drawContents(self):
        """
        first try to determine how best to fit the Dialog on
        screen, using the word length of the text and an
        estimate of 6 characters per word. once that's done,
        create some other Drawables and let them actually
        do the hard work of drawing.
        """

        if not self.touched:
            pass

        # set our size to the full screen (don't worry, we won't
        # draw over everything)
        (sh, sw) = self.getEngine().getScreenSize()
        self.setSize(0, 0, sh, sw)


        if type(self.text) in (types.ListType, types.TupleType):
            chars = sum([len(line) for line in self.text])
        else:
            chars = len(self.text)

        # to get a 4x3 ratio dialog box, we have to solve
        #  (4x) (3x) = chars
        #      12x^2 = chars
        #        x^2 = chars / 12
        #          x = sqrt(chars / 12)
        #
        # desired width is 4x
        width = 4.0 * math.sqrt(chars / 12.0)

        # min width of dialog is 1/2 screen width - 2 (for border)
        width = int(math.floor(max(width, 0.5 * (sw - 2)) + 0.5))
        self.log('width: %d' % width)

        wrapped = util.wrap(self.text, width)
        lines   = len(wrapped)

        # calculate screen positions
        height = 6 + lines

        y = (sh - height) / 2
        x = (sw - width)  / 2
        


        from Rows import Rows
        from Label import Label
        from TextEditor import TextEditor
        from Button import Button

        window = Rows(self, '%s:Window' % self.name, outerborder = True, innerborder = True)
        title  = Label(window, '%s:Window:Title' % self.name, text = self.title)
        window.addRow(title, 1, weight = 0)
        window.unbindKey('all')

        body   = Rows(window, '%s:Window:Body' % self.name, outerborder = False, innerborder = False)
        body.unbindKey('all')
        window.addRow(body, 1, weight = 1)

        tarea  = TextEditor(body, '%s:Window:Body:Message' % self.name, editable = False)
        tarea.setText(self.text)
        body.addRow(tarea, 1, weight = 1)

        blank  = Label(body, '%s:Window:Body:Blank' % self.name, '')
        body.addRow(blank, 1, weight = 0)

        ok     = Button(body, '%s:Window:Body:OK Button' % self.name, ' OK ')
        body.addRow(ok, 1, weight = 0)

        self.getEngine().pushFocus(ok)
        ok.bindKey('click', self.clickedOK)

        window.setSize(y, x, height, width)
        window.drawContents()


        self.untouch()
