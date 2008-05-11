import dtk
import curses
from dtktest import DtkTestCase

from dtk.events import Clicked


class BugThirtyFour(DtkTestCase):

    def testCallableClassBinding(self):

        call_trace = []

        class CallableClass(object):
            def __call__(self, event):
                call_trace.append(event)

        self.scr.set_input('enter','q')
        

        e = dtk.Engine()
        e.bindKey('q', e.quit)

        b = dtk.Button('blah')

        e.setRoot(b)

        mycallable = CallableClass()

        b.bindEvent(Clicked, mycallable)

        e.mainLoop()


        def map_of_counts(l):
            m = {}
            for elm in l:
                m[elm] = m.get(elm, 0) + 1
            return m

        self.assertEquals(1, len(call_trace), "same # of actual calls as expected")
        self.assertEquals('Clicked', call_trace[0].type, "expected 'Clicked', got %s" % call_trace[0].type)

