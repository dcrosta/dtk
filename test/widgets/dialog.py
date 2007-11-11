"""
test cases for the Dialog widget
"""

import dtk
import dtktest


class DialogTests(dtktest.DtkTestCase):

    def testDialogBasic(self):
        self.scr.set_input('enter','enter','q')

        event_log = []

        e = dtk.Engine()
        b = dtk.Button(text="Click me")
        
        def button_clicked():
            d = dtk.Dialog(
                    title='Dialog',
                    text='This is a dialog',
                    type='message'
                    )

            d.show()
            d.bindEvent('dismissed', lambda: event_log.append('dialog dismissed'))

        b.bindEvent('clicked', button_clicked)
        e.setRoot(b)

        e.bindKey('q',e.quit)
        e.mainLoop()

        
        self.assertTextAt(0, 0, '[Click me]', 1)
        self.assertTextAt(0, 0, '[Click me]', 2.1)

        # assert that the dialog was there after the first 'enter'
        self.assertTextAt(8,  20, '+-------------------------------------+', 1.1)
        self.assertTextAt(9,  20, '|Dialog                               |', 1.1)
        self.assertTextAt(10, 20, '|-------------------------------------|', 1.1)
        self.assertTextAt(11, 20, '|This is a dialog                     |', 1.1)
        self.assertTextAt(12, 20, '|                                     |', 1.1)
        self.assertTextAt(13, 20, '|[ OK ]                               |', 1.1)
        self.assertTextAt(14, 20, '+-------------------------------------+', 1.1)

        # assert that the dialog was not there after the second 'enter'
        self.assertTextAt(8,  20, '                                       ', 2.1)
        self.assertTextAt(9,  20, '                                       ', 2.1)
        self.assertTextAt(10, 20, '                                       ', 2.1)
        self.assertTextAt(11, 20, '                                       ', 2.1)
        self.assertTextAt(12, 20, '                                       ', 2.1)
        self.assertTextAt(13, 20, '                                       ', 2.1)
        self.assertTextAt(14, 20, '                                       ', 2.1)

