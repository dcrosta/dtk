"""
test cases for the Canvas widget
"""

import dtk
import dtktest


class CanvasTests(dtktest.DtkTestCase):

    def testDraw(self):
        self.scr.set_input('c','q')


        e = dtk.Engine()
        c = dtk.Canvas()
        e.setRoot(c)

        c.draw('hello, world!', 1, 1, bold=True)
        c.drawDown('ello sunshine!', 2, 1, foreground='yellow')

        # draws a box with a cross inside it
        c.box(5, 5, 3, 3)
        c.lineDown(5, 6, 3)
        c.line(6, 5, 3)

        c.bindKey('c', c.clear)
        c.bindKey('q', e.quit)

        e.mainLoop()


        # assert that the proper stuff is drawn at time = 1 tick
        self.assertTextAt(1, 1, 'hello, world!', 1)
        self.assertTextDownAt(1, 1, 'hello sunshine!', 1)

        self.assertTextAt(5, 5, '+|+', 1)
        self.assertTextAt(6, 5, '---', 1)
        self.assertTextAt(7, 5, '+|+', 1)


        # assert that at the end, everything is clear
        y, x = self.scr.getmaxyx()
        for i in xrange(y):
            self.assertTextAt(i, 0, ' ' * x)
