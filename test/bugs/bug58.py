import dtk
import dtktest


class BugFiftyEight(dtktest.DtkTestCase):

    def testInfiniteEventLoop(self):
        self.scr.set_input('enter', 'q')

        e = dtk.Engine()

        event_trace = []
        # a method which creates a new event whenever it receives one
        def dumb_event_target(_event_type, _source_obj):
            event_trace.append((_source_obj, _event_type))
            if len(event_trace) < 100:
                e.enqueueEvent(None, 'dummy event')


        b = dtk.Button()
        b.setText('Set the ball rolling')

        e.setRoot(b)

        b.bindEvent('clicked', dumb_event_target)
        e.bindEvent(None, 'dummy event', dumb_event_target)

        e.bindKey('q', e.quit)
        e.mainLoop()


        self.assertEquals(2, len(event_trace), "expected only 2 events, got %d" % len(event_trace))
        self.assertEquals((b, 'clicked'), event_trace[0])
        self.assertEquals((None, 'dummy event'), event_trace[1])
