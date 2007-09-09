import unittest
import sys
import os
import os.path

# add the path of this file to the python path, so that
# "import curses" picks up the test curses module
sys.path.insert( 0, os.path.abspath( os.path.dirname( __file__ ) ) )

# add the path to the locally checked out dtk module (one
# directory up) so that import dtk works and uses the local
# source, not any insalled site-package of the same name
sys.path.insert( 1, os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )


import curses
import dtk


class DtkTestCase(unittest.TestCase):

    def setUp(self):
        self.scr = curses.Screen(24, 80)
        curses._scr = self.scr
        curses.use_delay(False)
        curses.print_screen(False)

    def assertTextAt(self, y, x, text, time=None):
        t = self.scr.get_text_at(y, x, len(text), time)

        self.assertEquals(text, t, 'screen at (%d, %d) at time %g: "%s" != "%s"' % (y, x, time, text, t))


class TestBasics(DtkTestCase):

    def testHelloWorld(self):
        self.scr.set_input('q')

        class Canvas(dtk.Drawable):
            def __init__(self):
                super(Canvas, self).__init__()
            def render(self):
                self.draw('hello, world', 1, 1)

        e = dtk.Engine()
        e.setRoot(Canvas())
        e.bindKey('q', e.quit)
        e.mainLoop()

        self.assertTextAt(1, 1, 'hello, world', 1)


if __name__ == '__main__':
    unittest.main()
