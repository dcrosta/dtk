import dtk
import curses
from dtktest import DtkTestCase


class BugTwentySeven(DtkTestCase):

    def testStackPushTopChild(self):
        self.scr.set_input('q')

        e = dtk.Engine()

        s = dtk.Stack()

        l1 = dtk.Label('1')
        l1.name = 'L1'
        l2 = dtk.Label('2')
        l2.name = 'L2'

        s.push(l1)
        s.push(l2)

        e.setRoot(s)
        e.bindKey('q', e.quit)


        def pushPop(_source_obj):
            _source_obj.push(_source_obj.children[-1])

        s.bindKey('a', pushPop)
        e.mainLoop()
