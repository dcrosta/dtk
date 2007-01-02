import types
import math

import util
from core import Drawable, Container, InputContext

class Dialog(Container):
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

    def __init__(self, title = '', text = '', type = 'message', **kwargs):
        """
        Dialog constructor.

        @param parent: the parent Drawable
        @type  parent: dtk.Drawable

        """
        super(Dialog, self).__init__(**kwargs)

        self.kids = {}

        self.setTitle(text)
        self.setText(text)
        self.setType(type)

        self._setup()

        self.context = InputContext()


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
        self.window.touchAll()
        
        self.context.unquit()
        self.context.log = self.log
        self.context.setRoot(self)

        if self.type == 'message':
            self.context.setFocus(self.kids['ok'])

        elif self.type == 'yesno':
            self.context.setFocus(self.kids['yes'])

        else:
            self.context.setFocus(self.kids['input'])
        
        self.log.debug('activePath is: %s', [str(x) for x in self.context.root.getActivePath()])

        self.log.debug('beginning contextLoop')
        self.engine.contextLoop(self.context)
        self.log.debug('finished contextLoop')

        self.engine.touchAll()

    
    def _dismissed(self):
        """
        called when any button is clicked
        """
        self.context.quit()


    def _clickedOK(self):
        """
        called when the user clicks the 'OK' button in a message dialog
        """
        self.returned = True
        if self.type == 'input':
            self.result = self.kids['input'].getText()

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
        from Pager import Pager
        from TextField import TextField
        from Button import Button
        from core import Drawable

        self.window = Rows(outerborder = True, innerborder = False)
        self.window.name = 'Dialog::Window'
        self.window.unbindKey('all')

        self.kids['title'] = Label(text = self.title)
        self.kids['title'].name='Dialog::Title'
        self.window.addRow(self.kids['title'], fixedsize = 1)
        self.window.addSeparator(type = 'line')

        self.kids['tarea'] = Pager(editable = False)
        self.kids['tarea'].setText(self.text)
        self.kids['tarea'].name = 'Dialog::TArea'
        self.window.addRow(self.kids['tarea'], weight = 1)
        self.window.addSeparator(type = 'blank')

        self.kids['ok'] = None
        self.kids['yesno'] = None
        self.kids['yes'] = None
        self.kids['no'] = None

        if self.type == 'message':
            self.kids['ok'] = Button(' OK ')
            self.kids['ok'].name = 'Dialog::OKButton'
            self.kids['ok'].bindKey('click', self._clickedOK)

            self.window.addRow(self.kids['ok'], fixedsize = 1)

        elif self.type == 'input':
            self.kids['input'] = TextField()
            self.kids['input'].name = 'Dialog::InputField'
            self.kids['input'].bindKey('enter', self._clickedOK)

            self.window.addRow(self.kids['input'], fixedsize = 1)

        else:
            self.kids['yesno'] = Columns(outerborder = False, innerborder = False)

            self.kids['yes']   = Button(' Yes ')
            self.kids['yes'].name = 'Dialog::YesButton'
            self.kids['no']    = Button(' No ')
            self.kids['no'].name = 'Dialog::NoButton'

            self.kids['yes'].bindKey('click', self._clickedYes)
            self.kids['no'].bindKey('click',  self._clickedNo)

            self.kids['yesno'].addColumn(self.kids['yes'])
            self.kids['yesno'].addColumn(self.kids['no'])

            self.window.addRow(self.kids['yesno'], fixedsize = 1)


        # be a Container
        self.children = [self.window]
        self.active = self.window


    def setSize(self, y, x, h, w):
        if getattr(self, 'text', None)  is None or \
           getattr(self, 'title', None) is None or \
           getattr(self, 'type', None)  is None:
            #XXX: raise an exception
            return


        super(Dialog, self).setSize(y, x, h, w)


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
        
        self.window.setSize(y, x, height, width)

        self.touch()


    def drawContents(self):
        Drawable.drawContents(self)

        # delegate drawContents to the 'window' child
        self.window.drawContents()


    def render(self):
        self.clear()
        super(Dialog, self).render()
