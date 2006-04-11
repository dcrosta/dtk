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

    When the dialog is dismissed (by hitting "enter" on
    one of the buttons, depending on the type), it will
    create a psuedo-key, 'dismissed' which may be used
    as any other key (eg with bindKey).
    """

    def __init__(self, parent, name, title = '', text = '', type = 'message'):
        """
        Dialog constructor.

        @param parent: the parent Drawable
        @type  parent: dtk.Drawable

        """
        super(Dialog, self).__init__(parent, name)

        self.children = {}

        self.setTitle(text)
        self.setText(text)
        self.setType(type)

        self._setup()
    

    def setType(self, type):
        """
        sets the type of the dialog: 'message', 'yesno' or 'input'

        a 'message' dialog box displays the given text message
        with an 'OK' button to dismis the dialog.

        a 'yesno' dialog displays the given text message, and
        allows the user to choose a 'yes' or 'no' button. the
        getResult() method returns True if the user chose 'yes'
        or False if the user chose 'no'.

        an 'input' dialog displays the given text message and
        prompts the user for input with a text field.

        @param type: the type of the dialog, 'message', 'yesno'
            or 'input'
        @type  type: string
        """

        type = type.lower()
        self.returned = False

        if type in ('message', 'yesno', 'input'):
            self.type = type
        else:
            raise ValueError, "setType() expects 'message', 'yesno' or 'input' only"

        self._setup()
        self.touch()


    def getResult(self):
        """
        if the dialog has been dismissed, return the result the user
        chose, otherwise return None.

        in 'message' dialogs, the result is always True if the dialog
        has been dismissed. in 'yesno' dialogs, the result is True if
        the user chose 'yes', and False if the user chose 'no'. in
        'input' dialogs, returns the text entered by the user

        @return: for 'yesno' dialogs, True if the user chose 'yes',
            False if the user chose 'no'; for 'message' dialogs, 'True'
            if the user has closed the dialog; for 'input' dialogs,
            the string value entered by the user. for all types, None 
            if the dialog has not been dismissed yet
        @rtype: boolean, string or None
        """
        if self.returned:
            return self.result
        else:
            return None


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
        self._setup()
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
        self._setup()
        self.touch()


    def getTitle(self):
        """
        returns the title currently assigned to this Dialog

        @return: the title
        @rtype:  string or list of strings
        """
        return self.title

    
    def show(self):
        """
        shows the dialog
        """
        self.setSize(0, 0, 0, 0)
        self.touch()

        for child in self.children.values():
            if child is not None:
                child.touch()
        
        engine = self.getEngine()
        engine.pushFocus(self)

        if self.type == 'message':
            engine.pushFocus(self.children['ok'])
        elif self.type == 'input':
            engine.pushFocus(self.children['input'])
        else:
            engine.pushFocus(self.children['yes'])

    
    def _dismissed(self):
        """
        called when any button is clicked
        """
        self.getEngine().popFocus(self)

        self.handleInput('dismissed')


    def _clickedOK(self):
        """
        called when the user clicks the 'OK' button in a message dialog
        """
        self.returned = True
        if self.type == 'input':
            self.result = self.children['input'].getText()

        self._dismissed()


    def _clickedYes(self):
        """
        called when the user clicks the 'yes' button in a yesno dialog
        """
        self.returned = True
        self.result = True

        self._dismissed()


    def _clickedNo(self):
        """
        called when the user clicks the 'no' button in a yesno dialog
        """
        self.returned = True
        self.result = False

        self._dismissed()


    def _setup(self):
        """
        first try to determine how best to fit the Dialog on
        screen, using the word length of the text and an
        estimate of 6 characters per word. once that's done,
        create some other Drawables and let them actually
        do the hard work of drawing.
        """

        if getattr(self, 'text', None)  is None or \
           getattr(self, 'title', None) is None or \
           getattr(self, 'type', None)  is None:
            return



        from Rows import Rows
        from Columns import Columns
        from Label import Label
        from TextEditor import TextEditor
        from TextField import TextField
        from Button import Button

        self.children['window'] = Rows(self, '%s:Window' % self.name, outerborder = True, innerborder = True)
        self.children['title']  = Label(self.children['window'], '%s:Window:Title' % self.name, text = self.title)
        self.children['window'].addRow(self.children['title'], 1, weight = 0)
        self.children['window'].unbindKey('all')

        self.children['body']   = Rows(self.children['window'], '%s:Window:Body' % self.name, outerborder = False, innerborder = False)
        self.children['body'].unbindKey('all')
        self.children['window'].addRow(self.children['body'], 1, weight = 1)

        self.children['tarea']  = TextEditor(self.children['body'], '%s:Window:Body:Message' % self.name, editable = False)
        self.children['tarea'].setText(self.text)
        self.children['body'].addRow(self.children['tarea'], 1, weight = 1)

        self.children['blank']  = Label(self.children['body'], '%s:Window:Body:Blank' % self.name, '')
        self.children['body'].addRow(self.children['blank'], 1, weight = 0)

        self.children['ok'] = None
        self.children['yesno'] = None
        self.children['yes'] = None
        self.children['no'] = None

        if self.type == 'message':
            self.children['ok'] = Button(self.children['body'], '%s:Window:Body:OK Button' % self.name, ' OK ')
            self.children['ok'].bindKey('click', self._clickedOK)

            self.children['body'].addRow(self.children['ok'], 1, weight = 0)
            focus = self.children['ok']

        elif self.type == 'input':
            self.children['input'] = TextField(self.children['body'], '%s:Window:Body:Input' % self.name)
            self.children['input'].bindKey('enter', self._clickedOK)

            self.children['body'].addRow(self.children['input'], 1, weight = 0)

            focus = self.children['input']

        else:
            self.children['yesno'] = Columns(self.children['body'], '%s:Window:Body:YesNo' % self.name, outerborder = False, innerborder = False)

            self.children['yes']   = Button(self.children['yesno'], '%s:Window:Body:YesNo:Yes' % self.name, ' Yes ')
            self.children['no']    = Button(self.children['yesno'], '%s:Window:Body:YesNo:No' % self.name,  ' No ')

            self.children['yes'].bindKey('click', self._clickedYes)
            self.children['no'].bindKey('click',  self._clickedNo)

            self.children['yesno'].addColumn(self.children['yes'], 7)
            self.children['yesno'].addColumn(self.children['no'],  7)

            self.children['body'].addRow(self.children['yesno'], 1, weight = 0)
            focus = self.children['yes']


        self.setSize(self.y, self.x, self.h, self.w)


    def setSize(self, y, x, h, w):
        if getattr(self, 'text', None)  is None or \
           getattr(self, 'title', None) is None or \
           getattr(self, 'type', None)  is None:
            return



        # set our size to the full screen (don't worry, we won't
        # draw over everything)
        (self.h, self.w) = self.getEngine().getScreenSize()
        self.y = 0
        self.x = 0

        if self.h is None or self.w is None:
            return


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
        width = int(8.0 * math.sqrt(chars / 12.0))

        # min width of dialog is 1/2 screen width - 2 (for border)
        if width < (0.5 * (self.w - 2)):
            width = int(0.5 * (self.w - 2))

        wrapped = util.wrap(self.text, width)
        lines   = len(wrapped)

        # calculate screen positions
        height = 6 + lines

        y = (self.h - height) / 2
        x = (self.w - width)  / 2
        
        self.children['window'].setSize(y, x, height, width)

        self.touch()


    def drawContents(self):
        # delegate drawContents to the 'window' child
        self.children['window'].drawContents()


    def render(self):
        if not self.sizeSet(self):
            self.setSize(0, 0, 0, 0)
            self.sizeSet = True

        super(Dialog, self).render()
