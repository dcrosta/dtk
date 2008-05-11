import dtk
import dtktest

from dtk.events import Event, Clicked


class BugFiftyEight(dtktest.DtkTestCase):

    def testInfiniteEventLoop(self):

        class DummyEvent(Event):
            def __init__(self):
                Event.__init__(self, None)

        self.scr.set_input('enter', 'q')

        e = dtk.Engine()

        event_trace = []
        # a method which creates a new event whenever it receives one
        def dumb_event_target(event):
            event_trace.append((event.source, event.type))
            if len(event_trace) < 100:
                e.enqueueEvent(DummyEvent())


        b = dtk.Button()
        b.setText('Set the ball rolling')

        e.setRoot(b)

        b.bindEvent(Clicked, dumb_event_target)
        e.bindEvent(None, DummyEvent, dumb_event_target)

        e.bindKey('q', e.quit)
        e.mainLoop()

        self.assertEquals(2, len(event_trace), "expected 2 events, got %d" % len(event_trace))
        self.assertEquals((b, 'Clicked'), event_trace[0])
        self.assertEquals((None, 'DummyEvent'), event_trace[1])
